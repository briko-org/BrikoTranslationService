import os, sys, socket, time, pickle
from flask import Flask, flash, redirect, render_template, request, session, abort, json, jsonify, send_file, send_from_directory, abort, url_for
from api_params import Params
from utils.logger import set_logger
from utils.seglib import Split_Manual, Split_Nltk
import configs
AVAILABLE_LANGS = configs.AVAILABLE_LANGS
TRANSLATOR_PORT = configs.TRANSLATOR_PORT
HOST_ADD = configs.HOST_ADD

_MSGTYPE = "msgType"
_MSGID = "msgID"
_SOURCELANG = "sourceLang"
_REQUESTLANG = "requestLang"
_SOURCECONTENT = "sourceContent"
_MSGIDRESPONDTO = "msgIDRespondTo"
_MSGFLAG = "msgFlag"
_TRANSLATIONRESULTS = "translationResults"


_TRANS_MSG_TYPE = "Translation"
_STA_MSG_TYPE = "StatusCheck"
_TRANS_RESP_TYPE = "RespondTranslation"
_WRONG_MSG_TYPE = "Wrong msg type"
_BOT_MSG_PREFIX = "BOT"
_TRANS_MSG_PREFIX = "TRANS"
_SUCCESS_FLAG = "success"
_FAIL_FLAG = "failed"
_HEALTH_FLAG = "healthy"

_TRANS_RESPONSE = {
    _MSGTYPE : _TRANS_RESP_TYPE,
    _MSGID : "",
    _MSGIDRESPONDTO : "",
    _MSGFLAG : _FAIL_FLAG,
    _TRANSLATIONRESULTS : ""
}
_STATUS_RESPONSE = {
    _MSGTYPE : _STA_MSG_TYPE,
    _MSGID : "",
    _MSGIDRESPONDTO : "",
    _MSGFLAG : _HEALTH_FLAG
}

logger = set_logger("api_service.log")
def create_app():
    app = Flask(__name__)
    app.config.from_object(Params)
    
    @app.route('/', methods=['POST'])
    def index():
        return json.dumps({"found":"ok"})

    @app.route('/translator', methods=['POST'])
    def translator():
        if request.method == 'POST':            
            msgType = request.json[_MSGTYPE]
            msgID = request.json[_MSGID]
            resmsgID = str(msgID).replace(_BOT_MSG_PREFIX, _TRANS_MSG_PREFIX)

            if msgType == _TRANS_MSG_TYPE:
                sourceLang = request.json[_SOURCELANG]
                requestLang = request.json[_REQUESTLANG]
                sourceContent = request.json[_SOURCECONTENT]
                
                response_parcel = _TRANS_RESPONSE
                response_parcel[_MSGID] =resmsgID 
                response_parcel[_MSGIDRESPONDTO] = msgID
                translationresults={}
                logger.info(f'*** From {sourceLang} to {requestLang} ***')
                logger.info(f'*** Content: {sourceContent} ***')
                if sourceLang == "fr" or sourceLang == "en":
                    sourceList = Split_Nltk(sourceContent)
                else:
                    sourceList = Split_Manual(sourceContent)
                for sourceSentence in sourceList:
                    logger.info(f'*** Content sentence: {sourceSentence} ***')
                for reqLang in requestLang:
                    lang_pair = sourceLang + "_" + reqLang
                    if sourceLang in AVAILABLE_LANGS and reqLang in AVAILABLE_LANGS:
                        send_port = TRANSLATOR_PORT
                        parcel = {
                            "lang_pair" : lang_pair,
                            "content" : sourceList
                        }
                        try:
                            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_translator:
                                socket_translator.settimeout(240)
                                socket_translator.connect((HOST_ADD, send_port))
                                socket_translator.send(pickle.dumps(parcel))
                                from_translator = socket_translator.recv(1024)
                                translation = pickle.loads(from_translator)
                                socket_translator.close()

                                translation_parcel = {reqLang:translation}
                                logger.info(translation_parcel)
                                translationresults.update(translation_parcel)
                                response_parcel[_TRANSLATIONRESULTS] = translationresults
                        except Exception as ex:
                            logger.info(ex)
                            return json.dumps(response_parcel)
                    else:
                        logger.info(f'*** no model available for {lang_pair} ***')
                response_parcel[_MSGFLAG] = _SUCCESS_FLAG
                return json.dumps(response_parcel)
            elif msgType == "StatusCheck":
                #TODO: check service status
                return json.dumps(
                    {
                        _MSGTYPE:_STA_MSG_TYPE, 
                        _MSGID:resmsgID, 
                        _MSGIDRESPONDTO:msgID, 
                        _MSGFLAG:_HEALTH_FLAG
                    }
                )
            else:
                return json.dumps(
                    {
                        _MSGTYPE: msgType, 
                        _MSGID:resmsgID, 
                        _MSGIDRESPONDTO:msgID, 
                        _MSGFLAG:_WRONG_MSG_TYPE
                    }
                )
                
    return app      
app =  create_app()

if __name__ == "__main__":
    app.run()
