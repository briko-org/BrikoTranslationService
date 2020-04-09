from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os, sys, socket, select, time, pickle, validators, string, configs
import tempfile
import numpy as np
from six.moves import xrange
from absl import app as absl_app
from absl import flags
import tensorflow as tf
sys.path.append(configs._MODELS_PATH)
from official.transformer.utils import tokenizer
from official.utils.flags import core as flags_core
from official.utils.export import export
from official.transformer import transformer_main
#os.environ["CUDA_VISIBLE_DEVICES"] = "0"
_DECODE_BATCH_SIZE = configs._DECODE_BATCH_SIZE
_EXTRA_DECODE_LENGTH = configs._EXTRA_DECODE_LENGTH
_BEAM_SIZE = configs._BEAM_SIZE
_ALPHA = configs._ALPHA

_MODEL_PARAM_SET = configs._MODEL_PARAM_SET

_TOKEN = configs._TOKEN
_PRODUCTION_MODEL_PATH = configs._PRODUCTION_MODEL_PATH

_HOST_ADD = configs.HOST_ADD
_RECV_PORT = configs.TRANSLATOR_PORT

def _encode_and_add_eos(line, subtokenizer):
    return subtokenizer.encode(line) + [tokenizer.EOS_ID]

def _trim_and_decode(ids, subtokenizer):
    try:
        index = list(ids).index(tokenizer.EOS_ID)
        return subtokenizer.decode(ids[:index])
    except ValueError:
        return subtokenizer.decode(ids) 

def translate_list(vocab, model_dir, params, contentList, url_list = []):
    u_list = url_list
    translation_results = []
    url_count = 0
    
    subtokenizer = tokenizer.Subtokenizer(vocab)
    estimator = tf.estimator.Estimator(
        model_fn=transformer_main.model_fn, model_dir=model_dir,
        params=params)
    estimator_predictor = tf.contrib.predictor.from_estimator(estimator, export.build_tensor_serving_input_receiver_fn(shape=[None], dtype=tf.int32, batch_size=None))
    
    for content in contentList:
        # Replace URL with TOKENs
        content_split = content.split(' ')
        new_content_split = []
        for word in content_split:
            if validators.url(word):
                u_list.append(word)
                
                word = _TOKEN + str(url_count)
                url_count += 1
                
            new_content_split.append(word)
            content = ' '.join(new_content_split)
        try:
            tokens = _encode_and_add_eos(content, subtokenizer)
            predictions = estimator_predictor({"input":np.array([tokens],dtype=np.int32)})
            translation = _trim_and_decode(predictions["outputs"][0], subtokenizer)
            translation_results.append(translation)
             
        except:
            print("error in translation")
    
    return u_list, translation_results

def remove_space(txt):
    words = txt.split(' ')
    txt = words[0]
    words = words[1:]
    for word in words:
        end_en = txt[-1] in string.ascii_letters
        start_en = word[0] in string.ascii_letters
        if start_en and end_en:
            txt = txt + " "
        txt = txt + word
    return txt

def remove_brackets(txt):
    txt = txt.replace('-RSB- ','(').replace(' -LSB-',')')
    txt = txt.replace('-LCB- ','{').replace(' -RCB-','}')
    txt = txt.replace('-LRB- ','(').replace(' -RRB-',')')
    return txt
    
def remove_punct(txt):
    for mark in string.punctuation:
        txt = txt.replace(" " + mark, mark)
    return txt

def main(unused_argv):
    tf.logging.set_verbosity(tf.logging.INFO)

    socket_api = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_api.bind((_HOST_ADD, _RECV_PORT))
    socket_api.listen(5)
    while True:
        client_socket, _ = socket_api.accept()
        from_client = client_socket.recv(1024)
        parcel = pickle.loads(from_client)
        contentList = parcel["content"]
        lang_pair = parcel["lang_pair"]
        model_param = _MODEL_PARAM_SET
        params = transformer_main.PARAMS_MAP[model_param]
        params["beam_size"] = _BEAM_SIZE
        params["alpha"] = _ALPHA
        params["extra_decode_length"] = _EXTRA_DECODE_LENGTH
        params["batch_size"] = _DECODE_BATCH_SIZE
        
        #For language pairs that are not available yet, we use English as an 
        #intermediary language. i.e. from French to Chinese, the source is 
        #translated into English and then from English to Chinese.
        _MODEL_DIR = _PRODUCTION_MODEL_PATH + lang_pair
        if lang_pair == "fr_zh":
            _MODEL_DIR = _PRODUCTION_MODEL_PATH + "fr_en"
        elif lang_pair == "jp_zh":
            _MODEL_DIR = _PRODUCTION_MODEL_PATH + "jp_en"
        _VOCAB = _MODEL_DIR + "/vocab"
        url_list = []
        url_list, translation_results = translate_list(_VOCAB, _MODEL_DIR, params, contentList)

        if lang_pair == "fr_zh" or lang_pair == "jp_zh":
            _MODEL_DIR = _PRODUCTION_MODEL_PATH + "en_zh"
            _VOCAB = _MODEL_DIR + "/vocab"
            contentList = translation_results
            
            url_list, translation_results = translate_list(_VOCAB, _MODEL_DIR, params, contentList, url_list)
            
        translation_result = ' '.join(translation_results)
        
        # Post-Process Added
        if "_zh" in lang_pair:
            translation_result = remove_space(translation_result)
        translation_result = remove_brackets(translation_result)
        translation_result = remove_punct(translation_result)
                
        
        # Replace TOKENs with original URL
        if(len(url_list)>0):
            
            new_count = 0
            for _url in url_list:
                word = _TOKEN + str(new_count)
                translation_result = translation_result.replace(word, _url + " ") #extra space required for formatting 
                new_count += 1           
        
        try:
            client_socket.send(pickle.dumps(translation_result))
        except:
            print("error in sending")
        finally:
            client_socket.close()
                  
if __name__ == "__main__":
  absl_app.run(main)