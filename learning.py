#!/usr/bin/env python
# -*- coding: utf-8 -*-
#########################################################################
# Author: jonyqin
# Created Time: Thu 11 Sep 2014 01:53:58 PM CST
# File Name: ierror.py
# Description:定义错误码含义 
#########################################################################
WXBizMsgCrypt_OK = 0
WXBizMsgCrypt_ValidateSignature_Error = -40001
WXBizMsgCrypt_ParseXml_Error = -40002
WXBizMsgCrypt_ComputeSignature_Error = -40003
WXBizMsgCrypt_IllegalAesKey = -40004
WXBizMsgCrypt_ValidateCorpid_Error = -40005
WXBizMsgCrypt_EncryptAES_Error = -40006
WXBizMsgCrypt_DecryptAES_Error = -40007
WXBizMsgCrypt_IllegalBuffer = -40008
WXBizMsgCrypt_EncodeBase64_Error = -40009
WXBizMsgCrypt_DecodeBase64_Error = -40010
WXBizMsgCrypt_GenReturnXml_Error = -40011

root@ubuntu:/home/learning# cat learning.py
from WXBizMsgCrypt import WXBizMsgCrypt
from flask import Flask, request, make_response
import subprocess
import logging
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()

TOKEN = os.getenv("WX_TOKEN")
ENCODING_AES_KEY = os.getenv("WX_ENCODING_AES_KEY")
CORP_ID = os.getenv("WX_CORP_ID")

# 初始化加解密类
crypto = WXBizMsgCrypt(TOKEN, ENCODING_AES_KEY, CORP_ID)

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('werkzeug').setLevel(logging.DEBUG)


# 路由改成 /wechat_callback，与企业微信后台保持一致
@app.route('/wechat_callback', methods=['GET', 'POST'])
def wechat_callback():
    if request.method == 'GET':
        # 企业微信验证 URL
        msg_signature = request.args.get('msg_signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        echostr = request.args.get('echostr', '')

        logging.debug(f"GET params - msg_signature: {msg_signature}, timestamp: {timestamp}, nonce: {nonce}, echostr: {echostr}")
        ret, echo_str = crypto.VerifyURL(msg_signature, timestamp, nonce, echostr)
        logging.debug(f"VerifyURL ret: {ret}, echo_str: {echo_str}")
        if ret != 0:
            return "验证失败", 400

        response = make_response(echo_str)
        response.headers['Content-Type'] = 'text/plain'
        return response

    elif request.method == 'POST':
        # 企业微信发送消息
        msg_signature = request.args.get('msg_signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        xml_data = request.data

        logging.debug(f"POST params - msg_signature: {msg_signature}, timestamp: {timestamp}, nonce: {nonce}")
        logging.debug(f"POST data: {xml_data}")

        ret, decrypted_xml = crypto.DecryptMsg(xml_data, msg_signature, timestamp, nonce)
        logging.debug(f"DecryptMsg ret: {ret}, decrypted_xml: {decrypted_xml}")
        if ret != 0:
            return "解密失败", 400

        # 解析 XML
        xml_tree = ET.fromstring(decrypted_xml)
        msg_type = xml_tree.find('MsgType').text if xml_tree.find('MsgType') is not None else 'unknown'

        if msg_type == 'text':
            content = xml_tree.find('Content').text.strip()
            logging.info(f"收到文本消息: {content}")

            # 如果消息是 "nba"，直接执行 nba.py，不捕获输出
            if content.lower() == "start":
                try:
                    subprocess.Popen(["python3", "/home/learning/main.py"])
                    logging.info("已触发 main.py 执行")
                except Exception as e:
                    logging.error(f"执行 main.py 失败: {e}")
             
            if content.lower() == "sat":
                try:
                    subprocess.Popen(["python3", "/home/learning/sat.py"])
                    logging.info("已触发 sat.py 执行")
                except Exception as e:
                    logging.error(f"执行 sat.py 失败: {e}")
            
            if content.lower() == "bbc":
                try:
                    subprocess.Popen(["python3", "/home/learning/bbc.py"])
                    logging.info("已触发 bbc.py 执行")
                except Exception as e:
                    logging.error(f"执行 bbc.py 失败: {e}")
        else:
            logging.info(f"收到非文本消息，类型: {msg_type}")

        return "success"


if __name__ == '__main__':
    # 使用 0.0.0.0 允许公网访问
    app.run(host='0.0.0.0', port=8081, debug=True, threaded=True)
