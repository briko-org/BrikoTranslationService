import os, sys, string, inspect, re, json
from nltk.tokenize import sent_tokenize



def Split_Manual(string):
    SPLIT_SIGN = '%%%%'
    SIGN = '$PACK$'
    search_pattern = re.compile('\$PACK\$')
    pack_pattern = re.compile('(“.+?”|（.+?）|《.+?》|〈.+?〉|[.+?]|【.+?】|‘.+?’|「.+?」|『.+?』|".+?"|\'.+?\')')
    pack_queue = []
    pack_queue = re.findall(pack_pattern, string)
    string = re.sub(pack_pattern, SIGN, string)

    pattern = re.compile('(?<=[。？！])(?![。？！])')
    result = []
    while string != '':
        s = re.search(pattern, string)
        if s is None:
            result.append(string)
            break
        loc = s.span()[0]
        result.append(string[:loc])
        string = string[loc:]
    
    result_string = SPLIT_SIGN.join(result)
    while pack_queue:
        pack = pack_queue.pop(0)
        loc = re.search(search_pattern, result_string).span()
        result_string = result_string[:loc[0]] + pack + result_string[loc[1]:]

    return result_string.split(SPLIT_SIGN)


def Split_Nltk(str_input):
    str_result = sent_tokenize(str_input)
    return str_result

