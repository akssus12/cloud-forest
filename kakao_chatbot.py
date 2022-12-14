import re
import json
import pymysql
import os
import time
import pymongo
import secrets
import glob
import utils as ut

from flask import Flask, render_template, request, Response, stream_with_context, flash, make_response, session, jsonify
from flask_bootstrap import Bootstrap
# from flask_socketio import SocketIO, emit
from random import random
from utils import logger
from pytz import timezone
from streamer import RaonStreamer
from datetime import timedelta

# Fetch common configuration properties.
# When you modify config, you have to modify config.json

with open('config.json') as config_file:
    config_data = json.load(config_file)

flask_settings = config_data['flask_settings']
mysql_settings = config_data['mysql_settings']
mongo_settings = config_data['mongo_settings']

CAPTURE_PATH = flask_settings['CAPTURE_PATH']
SECRET_KEY = flask_settings['SECRET_KEY']
MYSQL_HOST = mysql_settings['MYSQL_HOST']
MYSQL_USER = mysql_settings['MYSQL_USER']
MYSQL_PASSWORD = mysql_settings['MYSQL_PASSWORD']
MYSQL_DB = mysql_settings['MYSQL_DB']
MYSQL_CHARSET = mysql_settings['MYSQL_CHARSET']
MONGO_HOST = mongo_settings['MONGO_HOST']
MONGO_DB = mongo_settings['MONGO_DB']
MONGO_COLLECTION = mongo_settings['MONGO_COLLECTION']

application = Flask(__name__)
secret_key_session = secrets.token_hex(16)
application.secret_key = secret_key_session

# Initialize CLASS file.
Bootstrap(application)
# Multi-threading RSTP Streaminer
streamer = RaonStreamer()

# Global variables to maintain whole source.
userid = ""
stream_src = ""

def stream_gen(src, userid, timer):
    streamObject = streamer.run(src)
    while streamObject:
        try:
            frame = streamer.bytescode(userid, timer)
            timer += 1
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.05)
        except GeneratorExit as e:
            logger.error("GeneratorExit RTPS : " + str(e))
            continue

@application.route('/stream')
def stream():
    src = stream_src
    timer = 0
    try:
        return Response(stream_with_context(stream_gen(src, userid, timer)),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print('[FlaskServer] ', 'stream error : ', str(e))

@application.route('/setNickname', methods=['POST'])
def set_nickname():
    nickNameByQuery = ""
    content = request.get_json()
    nickName = content['action']['params']['id_check_text']
    
    global userid
    userid = str(nickName)
    finalText = userid +"??? ???????????????. ???????????? ????????? ????????? ??????????????????!"
    dataSend = ut.kakaoResponse_SimpleText(finalText)
    return jsonify(dataSend)

@application.route('/getImageByNickname', methods=['POST'])
def get_image_nickname():
    if str(userid) == "":
        dataSend = ut.kakaoResponse_SimpleText("????????? ?????? ???????????? ??????????????????!")
    else:
        filepathByNickname = CAPTURE_PATH + userid + "/*"
        list_of_files = glob.glob(filepathByNickname) # * means all if need specific format then *.csv
        latest_file = max(list_of_files, key=os.path.getctime)
        # fullAbsoluteFilePath = CAPTURE_PATH + userid + "/" + latest_file

        splitByUrl = latest_file.split('/')
        finalImageUrl = "/" + splitByUrl[3] + "/" + splitByUrl[4]

        imageUrl = "http://133.186.228.38" + finalImageUrl # ???????????? ?????????!
        dataSend = ut.kakaoResponse_SimpleTextAndImage(imageUrl, "?????? ????????? ????????????.")

    return jsonify(dataSend)

@application.route('/getGaugeByNickname', methods=['POST'])
def get_gauge_nickname():
    logger.error("getGaugeByNickname get_gauge_nickname()")
    if str(userid) == "":
        dataSend = ut.kakaoResponse_SimpleText("????????? ?????? ???????????? ??????????????????!")
    else:
        temperature = ""
        humidity = ""
        logger.error("getGaugeByNickname mongodb")
        mongo_client = pymongo.MongoClient(MONGO_HOST)
        mongo_db = mongo_client[MONGO_DB]
        mongo_collection = mongo_db[MONGO_COLLECTION]

        gauge_raon = mongo_collection.find().limit(1).sort([('$natural',-1)])
        for gauge in gauge_raon:
            temperature = gauge["tmp"]
            humidity = gauge["hum"]
        finalText = "?????? ?????? ????????? ????????? " + str(temperature) + "???, ????????? " + str(humidity) + " ?????????."
        dataSend = ut.kakaoResponse_SimpleText(finalText)

    return jsonify(dataSend)

@application.route('/validateNickname', methods=['POST'])
def vaildate_nickname():
    validateNickname = ""
    validateStatus = ""
    content = request.get_json()
    nickName = content['value']['resolved']
    
    streamByJoinId_SQL = "SELECT joinid, stream FROM raonzena.joininfo WHERE joinid = '{}'".format(str(nickName))

    try:
        connection = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER,
                             password=MYSQL_PASSWORD, db=MYSQL_DB, charset=MYSQL_CHARSET, autocommit=True)
        with connection.cursor() as curs:
            curs.execute(streamByJoinId_SQL)
            result = curs.fetchone()
            validateNickname = result[0]
    except Exception as e:
        logger.error("login check error " + str(e))
    finally:
        connection.close()

    if str(validateNickname) != "":
        validateStatus = "SUCCESS"
    else:
        validateStatus = "FAIL"
        
    dataSend = {
        "status": validateStatus
    }

    return jsonify(dataSend)

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
