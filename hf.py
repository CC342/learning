#!/usr/bin/env python3
import requests
import time
import jwt  # pip install pyjwt


# ===================== 填写你的信息 =====================
KEY_ID = "jwtid"          # 控制台凭据ID
PROJECT_ID = "项目id"      # 控制台项目ID
PRIVATE_KEY = """你的私钥"""   # PEM格式Ed25519私钥
API_HOST = "你的api—host"
LOCATION = "地区编码"         # 查看和风官网
CITY_NAME = "城市·区" 
# =======================================================

# 生成JWT
def generate_jwt(key_id, project_id, private_key):
    now = int(time.time())
    payload = {
        "sub": project_id,
        "iat": now,
        "exp": now + 3600
    }
    headers = {
        "alg": "EdDSA",
        "kid": key_id
    }
    token = jwt.encode(payload, private_key, algorithm="EdDSA", headers=headers)
    return token

# 获取天气数据
def get_weather():
    token = generate_jwt(KEY_ID, PROJECT_ID, PRIVATE_KEY)
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://{API_HOST}/v7/weather/now?location={LOCATION}&gzip=true&lang=zh"
    res = requests.get(url, headers=headers, timeout=10)
    return res.json()

# 获取空气质量
def get_air_quality():
    token = generate_jwt(KEY_ID, PROJECT_ID, PRIVATE_KEY)
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://{API_HOST}/v7/air/now?location={LOCATION}&gzip=true&lang=zh"
    res = requests.get(url, headers=headers, timeout=10)
    return res.json()

# 天气图标
def weather_icon(text):
    icons = {
        "晴": "☀️", "多云": "⛅", "阴": "☁️",
        "雨": "🌧️", "雪": "❄️", "雷": "⛈️",
    }
    for k in icons:
        if k in text:
            return icons[k]
    return "🌡️"

# 空气质量等级
def air_icon(category):
    icons = {
        "优": "🟢", "良": "🟡",
        "轻度污染": "🟠", "中度污染": "🔴",
        "重度污染": "🟣", "严重污染": "⚫",
    }
    return icons.get(category, "❓")

# 打印天气信息
def print_weather(weather_info, air_info):
    now = weather_info.get("now", {})
    air_now = air_info.get("now", {})

    print(f"=== {CITY_NAME} 天气与空气质量 ===")
    print(f"数据更新时间: {weather_info.get('updateTime','无数据')}  |  空气更新时间: {air_info.get('updateTime','无数据')}")
    #print(f"天气链接: {weather_info.get('fxLink','无链接')}")
    #print(f"空气质量链接: {air_info.get('fxLink','无链接')}")
    print("-" * 50)

    print(f"{weather_icon(now.get('text',''))} 天气: {now.get('text','无数据')}")
    print(f"温度: {now.get('temp','无数据')} ℃  |  体感温度: {now.get('feelsLike','无数据')} ℃")
    print(f"降水量: {now.get('precip','无数据')} mm")
    print(f"风向: {now.get('windDir','无数据')}  风力: {now.get('windScale','无数据')}级  风速: {now.get('windSpeed','无数据')} km/h")
    print(f"湿度: {now.get('humidity','无数据')} %  |  气压: {now.get('pressure','无数据')} hPa")
    print(f"能见度: {now.get('vis','无数据')} km  |  云量: {now.get('cloud','无数据')} %  |  露点: {now.get('dew','无数据')} ℃")
    
    print("\n空气质量:")
    print(f"{air_icon(air_now.get('category',''))} AQI: {air_now.get('aqi','无数据')}  |  主要污染物: {air_now.get('primary','无数据')}  |  空气等级: {air_now.get('category','无数据')}")
    print("-" * 50)

if __name__ == "__main__":
    try:
        weather_info = get_weather()
        air_info = get_air_quality()
        
        if weather_info.get("code") != "200" or "now" not in weather_info:
            raise ValueError("获取天气失败或返回格式异常")
        if air_info.get("code") != "200" or "now" not in air_info:
            raise ValueError("获取空气质量失败或返回格式异常")

        print_weather(weather_info, air_info)

    except Exception as e:
        print("获取数据失败:", e)

