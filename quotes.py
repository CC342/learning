import requests
from datetime import datetime

def get_daily_quote():
    try:
        # 从 ZenQuotes 获取每日一句
        response = requests.get("https://zenquotes.io/api/today")
        data = response.json()
        quote = data[0]["q"]
        author = data[0]["a"]
        return quote, author
    except Exception as e:
        print(f"获取每日名言失败: {e}")
        return None, None

def translate_to_chinese(text):
    try:
        # 使用 MyMemory 免费翻译 API（无需注册）
        url = "https://api.mymemory.translated.net/get"
        params = {"q": text, "langpair": "en|zh-CN"}
        response = requests.get(url, params=params)
        data = response.json()
        translation = data["responseData"]["translatedText"]
        return translation
    except Exception as e:
        print(f"翻译失败: {e}")
        return "（翻译失败）"

def main():
    quote, author = get_daily_quote()
    if not quote:
        return

    translation = translate_to_chinese(quote)

    print(f"🌞 每日一句 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("──────────────────────────────")
    print(f"💬 英文: {quote}")
    print(f"🇨🇳 中文: {translation}")
    print(f"📝 作者: {author}")
    print("──────────────────────────────")

if __name__ == "__main__":
    main()

