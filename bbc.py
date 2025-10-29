#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
from dotenv import load_dotenv


load_dotenv() 

# ===================== 企业微信 & Telegram 推送 =====================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WX_CORP_ID = os.getenv("WX_CORP_ID")
WX_AGENT_ID = os.getenv("WX_AGENT_ID")
WX_SECRET = os.getenv("WX_SECRET")

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

# ===================== BBC 新闻抓取 =====================
BBC_HOME = "https://www.bbc.com/news"

def fetch_headline_article():
    res = requests.get(BBC_HOME, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    
    main_content = soup.find("main", id="main-content")
    if not main_content:
        raise Exception("抓取失败: 无法找到 <main id='main-content'>")
    
    first_article_link = main_content.find("a")
    if not first_article_link or not first_article_link.get("href"):
        raise Exception("抓取失败: 无法找到头条新闻链接")
    
    href = first_article_link["href"]
    if href.startswith("http"):
        article_url = href
    else:
        article_url = "https://www.bbc.com" + href
 
    res_article = requests.get(article_url, timeout=10)
    res_article.raise_for_status()
    soup_article = BeautifulSoup(res_article.text, "html.parser", from_encoding="utf-8")
    
    title_tag = soup_article.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else first_article_link.get_text(strip=True)
    
    content = []
    signature = []
    
    article_tag = soup_article.find("article")
    if article_tag:
        paragraphs = article_tag.find_all("p")
    else:
        paragraphs = soup_article.find_all("p")
    
    for p in paragraphs:
        text = p.get_text(strip=True)
        if not text:
            continue
        if any(keyword in text for keyword in ["Copyright", "BBC is not responsible", "Read about our approach"]):
            continue
        if text.startswith("With additional reporting by") or text.startswith("By "):
            signature.append(text)
            continue
        content.append(text)
    
    return title, article_url, content, signature

def format_article_for_push(title, link, content, signature):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sep = ""
    msg = sep
    msg += f"🌐 BBC 头条新闻  |  更新时间: {now}\n"
    msg += "="*27 + "\n"
    msg += f"📰 标题: {title}\n"
    msg += f"🔗 链接: {link}\n"
    msg += "-"*52 + "\n"
    msg += "📖 正文:\n\n"
    for para in content:
        msg += f"{para}\n\n"
    if signature:
        for para in signature:
            msg += f"{para}\n"
    msg += sep
    return msg

# ===================== 主程序 =====================
if __name__ == "__main__":
    try:
        title, link, content, signature = fetch_headline_article()
        msg = format_article_for_push(title, link, content, signature)
        print(msg)  # 控制台打印
        
        # 推送到 Telegram 和企业微信
        try:
            send_telegram(msg)
            send_wechat(msg)
        except Exception as e:
            print(f"❌ 推送失败: {e}")
            
    except Exception as e:
        print("抓取失败:", e)
