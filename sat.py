import json
import random
from datetime import datetime
import requests
import os
import re
from dotenv import load_dotenv

# 配置

# 本地题库文件路径
QUESTION_FILE = "/home/learning/questions.json"

# 读取 .env 配置
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WX_CORP_ID = os.getenv("WX_CORP_ID")
WX_AGENT_ID = os.getenv("WX_AGENT_ID")
WX_SECRET = os.getenv("WX_SECRET")

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

# 数据加载与随机抽题
def load_questions():
    """加载本地 JSON 文件"""
    with open(QUESTION_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    all_questions = []
    # 支持多类型题库，如 math、reading、writing 等
    for category, questions in data.items():
        all_questions.extend(questions)
    return all_questions

def pick_random_question(questions):
    """随机选一道题"""
    return random.choice(questions)

# 显示题目（文本化处理）
def display_question(q):
    """美观地显示题目、选项和解析"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    question_raw = q["question"]["question"]
    choices_raw = q["question"]["choices"]  # 预计为字典 {"A": "...", "B": "...", ...}
    explanation_raw = q["question"]["explanation"]
    domain = q.get("domain", "未知分类")
    difficulty = q.get("difficulty", "未知难度")

    if USE_LATEX_TEXT:
        question = latex_to_text(question_raw)
        choices = {k: latex_to_text(v) for k, v in choices_raw.items()}
        explanation = latex_to_text(explanation_raw)
    else:
        question = question_raw
        choices = choices_raw
        explanation = explanation_raw

    correct = q["question"]["correct_answer"]

    msg = ""
    msg += f"📘 SAT 每日一题  |  更新时间: {now}\n"
    msg += "=" * 27 + "\n"
    msg += f"📚 分类: {domain}   \n💡 难度: {difficulty}\n"
    msg += "-" * 52 + "\n"
    msg += f"📝 题目：\n{question}\n"
    for key in ["A", "B", "C", "D"]:
        val = choices.get(key, "")
        msg += f"  {key}. {val}\n"
    msg += "-" * 52 + "\n"
    msg += f"✅ 正确答案: {correct}\n"
    msg += f"🧩 解析: {explanation}\n"
    msg += ""
    return msg

# 发送机制
def send_telegram(msg):
    """通过 Telegram 发送消息"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.get(url, params={"chat_id": TELEGRAM_CHAT_ID, "text": msg})

def send_wechat(msg):
    """通过企业微信发送消息"""
    token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={WX_CORP_ID}&corpsecret={WX_SECRET}"
    r = requests.get(token_url).json()
    access_token = r.get("access_token")
    if not access_token:
        print("❌ 企业微信获取 access_token 失败")
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

# 主执行入口
if __name__ == "__main__":
    try:
        questions = load_questions()
        q = pick_random_question(questions)
        msg = display_question(q)

        print(msg)

        send_telegram(msg)
        send_wechat(msg)

    except Exception as e:
        print("❌ 出错了:", e)
