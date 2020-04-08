# Briko Translation Service
Briko Translation Service Based on Tensorflow Transformer Translation Model
## Introduction

This is a translation service built on Tensorflow transformer translation model ([ver: r1.13.0](https://github.com/tensorflow/models/tree/r1.13.0/official/transformer)).

It is part of our COVID-19 News Bot on Telegram Project, you can find more about this project [here](https://github.com/briko-org/document/blob/master/Briko_Telegram_News_Bot_EN.md). 

We have trained several translator models using the existing open-source corpus and this service can be used as an API server, based on [Flask](https://flask.palletsprojects.com/en/1.1.x/), to host these translator models. This server can be used in junction with applications such as a [Telegram bot](https://github.com/briko-org/brikobot) to provide multi-language machine translation capabilities.

While we do not dive into the details of the transformer architecture or the process of model training here, we highly recommend you to read this paper [Attention is All You Need](https://arxiv.org/abs/1706.03762) and the [training walkthrough](https://github.com/tensorflow/models/tree/r1.13.0/official/transformer#walkthrough) if you are interested and like to learn more about it.

## System Environment
This repo is developed and tested on:

|System| CUDA|Python|Tensorflow|
|---|---|---|---|---|
|18.04.2 LTS|10.2|3.6.8|1.13.2|




## Walkthrough

Before you start, please clone this repository, preferably into your existing transformer rep:.
```
/path/to/models/offcial/transformer/
```
There are a few dependencies need to be installed, please run:
```
pip install -r requirements.txt
```
Please remember to modify ```config.py``` to match your setup environment. To start the server, run the following script:
```
./run_services.sh
```
* Please note that the model checkpoints as well as the vocab file are assumed to be placed in _PRODUCTION_MODEL_PATH.

## Appendix

### API Address
```
0.0.0.0:1234/translator
```
###  Translation Request:
```python
{
    "msgType": "Translation",
    "msgID" : "BOT00012234",
    "sourceLang" : "en",
    "requestLang" : ["zh","fr"],
    "sourceContent" : "this is a test."
}
```
### Response:

#### Successful:
```python
{
    "msgType": "RespondTranslation",
    "msgID" : "TRANS00012",
    "msgIDRespondTo" : "BOT00012234",
    "msgFlag" : "success",
    "translationResults": {"fr": "C'est un test.", "zh": "\u8fd9 \u662f \u4e00 \u4e2a \u6d4b\u8bd5 \u3002"}
}
```
#### Failed:
```python
{
    "msgType": "RespondTranslation",
    "msgID" : "TRANS00012",
    "msgIDRespondTo" : "BOT00012234",
    "msgFlag" : "failed",
    "translationResults" : ""
}
```

### Status Check Request:
```python
{
    "msgType": "StatusCheck",
    "msgID" : "BOT000002"
}
```
#### Healthy:
```python
{
    "msgType": "StatusCheck",
    "msgID" : "TRANS00235",
    "msgIDRespondTo" : "BOT000002",
    "msgFlag" : "healthy"
}
```

## Wrong Request Response:
```python
{
    "msgType": "I have an apple.",
    "msgID" : "BOT00012234",
    "sourceLang" : "en",
    "requestLang" : "jp",
    "sourceContent" : "I have an apple."
}
```
### Response:
```python
{
    "msgType": "I have an apple.",
    "msgID" : "TRANS00235",
    "msgIDRespondTo" : "BOT00012234",
    "msgFlag" : "Wrong msg type"
}
```

##  License:

[MIT](LICENSE)