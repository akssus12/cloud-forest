# -*- coding: utf-8 -*-
import logging
import json

# log initiation
logger = logging.getLogger()

# log level
logger.setLevel(logging.ERROR)

# log format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

def kakaoResponse_SimpleText(text):
    dataSend = {
        "version" : "2.0",
        "template" : {
            "outputs" : [
                {
                    "simpleText" : {
                        "text" : text
                    }
                }
            ]
        }
    }
    return dataSend

def kakaoResponse_SimpleTextAndImage(imageUrl, text):
    dataSend = {
        "version" : "2.0",
        "template" : {
            "outputs" : [
                {
                    "simpleImage": {
                        "imageUrl": imageUrl,
                        "altText": text
                    }
                }
            ]
        }
    }
    return dataSend

