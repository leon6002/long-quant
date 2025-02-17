import execjs
def hexin():
    #获取hexin-v
    with open("src/crawlers/js/wen.js", "r", encoding="utf-8") as f:
        js = f.read()
    JS = execjs.compile(js)  # 读取时间拼接进入js代码中
    hexin = JS.call("rt.update")
    return hexin

def headers():
    return {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9",
        "hexin-v": hexin(),
        "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "referrer": "https://news.10jqka.com.cn/realtimenews.html",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }

def get_headers():
    return {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9",
        "hexin-v": hexin(),
        "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }