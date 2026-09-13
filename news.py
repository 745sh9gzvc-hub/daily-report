import os
import requests
import akshare as ak
import feedparser
from datetime import datetime

# ============ 配置区 ============
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN")
# ================================

def get_us_stock():
    """获取美股三大指数行情"""
    try:
        df = ak.index_us_stock_sina()
        targets = {'道琼斯': '.DJI', '纳斯达克': '.IXIC', '标普500': '.INX'}
        res = []
        for _, row in df.iterrows():
            if row['symbol'] in targets.values():
                name = [k for k, v in targets.items() if v == row['symbol']][0]
                price = row.get('current_price', 'N/A')
                pct = row.get('change_percent', 'N/A')
                res.append(f"· {name}: {price} ({pct}%)")
        return res
    except Exception as e:
        return [f"美股数据获取失败: {e}"]

def get_news():
    """获取 Yahoo Finance 最新新闻标题"""
    try:
        feed = feedparser.parse("https://finance.yahoo.com/news/rssindex")
        news = []
        for entry in feed.entries[:5]:
            news.append(f"· {entry.title}")
        return news
    except Exception as e:
        return [f"新闻获取失败: {e}"]

def build_report():
    """构建早间要闻内容"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"🌍 每日早间全球要闻 · {now}", ""]
    
    lines.append("【① 美股隔夜走势】")
    lines.extend(get_us_stock())
    lines.append("")
    
    lines.append("【② 最新财经新闻】")
    lines.extend(get_news())
    lines.append("")
    
    lines.append("⚠️ 注：此为自动抓取的基础版。如需按重要性排序并标注影响，请配置 AI 接口。")
    return "\n".join(lines)

def push_to_wechat(title, content):
    """通过 PushPlus 推送到微信"""
    url = "http://www.pushplus.plus/send"
    payload = {
        "token": PUSHPLUS_TOKEN,
        "title": title,
        "content": content,
        "template": "txt",
    }
    resp = requests.post(url, json=payload)
    print(resp.json())

if __name__ == "__main__":
    report = build_report()
    push_to_wechat("每日早间全球要闻", report)
