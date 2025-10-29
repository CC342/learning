#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import requests
import time
import jwt  
import json
import random
from datetime import datetime
from dotenv import load_dotenv
import os
import cnlunar
from cnlunar.holidays import legalHolidaysDic, legalLunarHolidaysDic, otherHolidaysList, otherLunarHolidaysList

load_dotenv()  # 加载 .env 文件

# ===================== 配置 =====================
KEY_ID = "jwtid"
PROJECT_ID = "项目id"
PRIVATE_KEY = """你的私钥"""
API_HOST = "你的api-host"
LOCATION = "城市代码"       #查看和风官网
CITY_NAME = "城市·区"
QUESTION_FILE = "/home/learning/questions.json"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WX_CORP_ID = os.getenv("WX_CORP_ID")
WX_AGENT_ID = os.getenv("WX_AGENT_ID")
WX_SECRET = os.getenv("WX_SECRET")

# ===================== JWT生成 =====================
def generate_jwt(key_id, project_id, private_key):
    now = int(time.time())
    payload = {"sub": project_id, "iat": now, "exp": now + 3600}
    headers = {"alg": "EdDSA", "kid": key_id}
    token = jwt.encode(payload, private_key, algorithm="EdDSA", headers=headers)
    return token

# ===================== 天气信息 =====================
def get_weather():
    token = generate_jwt(KEY_ID, PROJECT_ID, PRIVATE_KEY)
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://{API_HOST}/v7/weather/now?location={LOCATION}&gzip=true&lang=zh"
    return requests.get(url, headers=headers, timeout=10).json()

def get_air_quality():
    token = generate_jwt(KEY_ID, PROJECT_ID, PRIVATE_KEY)
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://{API_HOST}/v7/air/now?location={LOCATION}&gzip=true&lang=zh"
    return requests.get(url, headers=headers, timeout=10).json()

def weather_icon(text):
    icons = {"晴":"☀️","多云":"⛅","阴":"☁️","雨":"🌧️","雪":"❄️","雷":"⛈️"}
    for k in icons:
        if k in text:
            return icons[k]
    return "🌡️"

def air_icon(category):
    icons = {"优":"🟢","良":"🟡","轻度污染":"🟠","中度污染":"🔴","重度污染":"🟣","严重污染":"⚫"}
    return icons.get(category, "❓")

def format_weather(weather_info, air_info):
    now = weather_info.get("now", {})
    air_now = air_info.get("now", {})
    text = f"天气: {now.get('text','无数据')}\n"
    text += f"温度: {now.get('temp','无数据')} ℃  |  体感温度: {now.get('feelsLike','无数据')} ℃\n"
    text += f"降水量: {now.get('precip','无数据')} mm\n"
    text += f"风向: {now.get('windDir','无数据')}  风力: {now.get('windScale','无数据')}级  风速: {now.get('windSpeed','无数据')} km/h\n"
    text += f"湿度: {now.get('humidity','无数据')} %  |  气压: {now.get('pressure','无数据')} hPa\n"
    text += f"能见度: {now.get('vis','无数据')} km  |  云量: {now.get('cloud','无数据')} %  |  露点: {now.get('dew','无数据')} ℃\n\n"
    text += "空气质量:\n"
    text += f"{air_icon(air_now.get('category',''))} AQI: {air_now.get('aqi','无数据')}  |  主要污染物: {air_now.get('primary','无数据')}  |  空气等级: {air_now.get('category','无数据')}\n"
    text += "-"*30 + "\n\n"
    return text

# ===================== 农历信息 =====================
def get_lunar_info():
    today = datetime.today()
    a = cnlunar.Lunar(today)
    
    def check_legal_holiday(date):
        if (date.month, date.day) in legalHolidaysDic:
            return legalHolidaysDic[(date.month, date.day)]
        lunar_month_day = (a.lunarMonth, a.lunarDay)
        if lunar_month_day in legalLunarHolidaysDic:
            return legalLunarHolidaysDic[lunar_month_day]
        for month_day_dict in otherHolidaysList:
            if date.month in month_day_dict and date.day == month_day_dict[date.month]:
                return month_day_dict[date.month]
        return None

    def check_other_lunar_holiday(date):
        lunar_month_day = (a.lunarMonth, a.lunarDay)
        for month_day_dict in otherLunarHolidaysList:
            if lunar_month_day in month_day_dict:
                return month_day_dict[lunar_month_day]
        return None

    legal_holiday = check_legal_holiday(today)
    other_lunar_holiday = check_other_lunar_holiday(today)
    
    dic = {
        '日期': today.strftime('%Y-%m-%d'),
        '农历': f"{a.lunarYearCn} {a.year8Char}[{a.chineseYearZodiac}]年 {a.lunarMonthCn}{a.lunarDayCn}"
    }
    
    if a.todaySolarTerms and a.todaySolarTerms != "无":
        dic['节气'] = a.todaySolarTerms
    if legal_holiday:
        dic['法定节假日'] = legal_holiday
    if other_lunar_holiday:
        dic['农历节假日'] = other_lunar_holiday

    lunar_info = ""
    for key, value in dic.items():
        lunar_info += f"{key}: {value}\n"
    
    return lunar_info

# ===================== 每日一句 =====================
def get_daily_quote():
    try:
        response = requests.get("https://zenquotes.io/api/today")
        data = response.json()
        quote = data[0]["q"]
        author = data[0]["a"]
        return quote, author
    except:
        return "无数据", "无数据"

def translate_to_chinese(text):
    try:
        url = "https://api.mymemory.translated.net/get"
        params = {"q": text, "langpair": "en|zh-CN"}
        res = requests.get(url, params=params)
        return res.json()["responseData"]["translatedText"]
    except:
        return "无数据"

def format_quote():
    en, author = get_daily_quote()
    cn = translate_to_chinese(en)
    text = f"🌞 每日一句\n\n"
    text += f"英文: {en}\n\n中文: {cn}\n\n作者: {author}\n\n"
    return text

# ===================== SAT题 =====================
# 开关：是否对 LaTeX 进行文本化处理
USE_LATEX_TEXT = True

def latex_to_text(s: str) -> str:
    """将 LaTeX 表达式转换为可读文本形式，可扩展"""
    if not isinstance(s, str):
        return s
    # 分式: \frac{a}{b} -> a/b
    s = re.sub(r"\\frac\{([^}]*)\}\{([^}]*)\}", r"\1/\2", s)
    # 括号替换
    s = s.replace(r"\left(", "(").replace(r"\right)", ")")
    # 行内/块公式标记移除
    s = re.sub(r"\$\$(.*?)\$\$", r"\1", s)
    s = re.sub(r"\$(.*?)\$", r"\1", s)
    # 根号 sqrt
    s = re.sub(r"\\sqrt\{([^}]*)\}", r"sqrt(\1)", s)
    # 乘号
    s = s.replace(r"\cdot", "*").replace(r"\times", "*")
    # 常见关系符号
    s = s.replace(r"\le", "<=").replace(r"\ge", ">=")
    s = s.replace(r"\neq", "!=").replace(r"\approx", "approx")
    # 常用希腊字母
    s = s.replace(r"\pi", "pi")
    # 分隔符处理
    s = s.replace(r"\,", " ").replace(r"\;", " ")
    # 去除多余反斜杠
    s = s.replace("\\", "")
    return s

def load_questions():
    with open(QUESTION_FILE,"r",encoding="utf-8") as f:
        data = json.load(f)
    all_q = []
    for k,v in data.items():
        all_q.extend(v)
    return all_q

def pick_random_question(questions):
    return random.choice(questions)

def format_sat():
    try:
        questions = load_questions()
        q = pick_random_question(questions)
        question = q["question"]["question"]
        choices = q["question"]["choices"]
        correct = q["question"]["correct_answer"]
        explanation = q["question"]["explanation"]
        domain = q.get("domain","无数据")
        difficulty = q.get("difficulty","无数据")
        
        if USE_LATEX_TEXT:
            question = latex_to_text(question)
            choices = {k: latex_to_text(v) for k, v in choices.items()}
            explanation = latex_to_text(explanation)
        else:
            question = question
            choices = choices
            explanation = explanation 
        
        text = "="*27 + "\n"
        text += f"📘 SAT 每日一题 | 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        text += "-"*30 + "\n"
        text += f"📚 分类: {domain}\n💡 难度: {difficulty}\n"
        text += "-"*30 + "\n\n"
        text += f"题目:\n{question}\n"
        for k,v in choices.items():
            text += f"  {k}. {v}\n"
        text += "-"*30 + "\n\n"
        text += f"✅ 正确答案: {correct}\n"
        text += f"🧩 解析: {explanation}\n"
        text += ""
        return text
    except:
        return "📘 SAT 每日一题: 无数据\n"

# ===================== 推送函数 =====================
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.get(url, params={"chat_id": TELEGRAM_CHAT_ID, "text": msg})

def send_wechat(msg):
    token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={WX_CORP_ID}&corpsecret={WX_SECRET}"
    r = requests.get(token_url).json()
    access_token = r.get("access_token")
    if not access_token:
        print("企业微信获取access_token失败")
        return
    send_url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"
    data = {
        "touser": "@all",
        "msgtype": "text",
        "agentid": int(WX_AGENT_ID),
        "text": {"content": msg},
        "safe": 0
    }
    requests.post(send_url, json=data)

# ===================== 主程序 =====================
if __name__ == "__main__":
    push_msg = ""
    
    # 日历信息
    #push_msg += get_lunar_info() + "\n"
    
    # 天气信息
    try:
        weather_info = get_weather()
        air_info = get_air_quality()
        push_msg += f"======== {CITY_NAME} =======\n"
        push_msg += get_lunar_info() + "\n"
        push_msg += format_weather(weather_info, air_info)
    except Exception as e:
        push_msg += f"❌ 获取天气失败: {e}\n"
    
    # 每日一句
    push_msg += format_quote()
    
    # SAT题
    push_msg += format_sat()
    
    # 控制台打印
    print(push_msg)
    
    # 推送
    try:
        send_telegram(push_msg)
        send_wechat(push_msg)
    except Exception as e:
        print(f"❌ 推送失败: {e}")
