import os
import requests
import akshare as ak
from datetime import datetime

# ============ 配置区 ============
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN")
# ================================

def get_stock_data():
    """获取上证指数、深证成指、创业板指行情"""
    try:
        df = ak.stock_zh_index_spot_em(symbol="沪深重要指数")
        target = {
            "000001": "上证指数",
            "399001": "深证成指",
            "399006": "创业板指",
        }
        result = []
        for _, row in df.iterrows():
            code = str(row["代码"])
            if code in target:
                result.append({
                    "名称": target[code],
                    "最新价": row["最新价"],
                    "涨跌幅": row["涨跌幅"],
                    "成交量": row.get("成交量", "N/A"),
                    "成交额": row.get("成交额", "N/A"),
                })
        return result
    except Exception as e:
        return [{"错误": f"获取行情失败: {e}"}]

def build_report():
    """构建日报内容"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"📊 A股行情日报 · {now}", ""]

    weekday = datetime.now().weekday()
    if weekday >= 5:
        lines.append("⚠️ 今日为周末，A股休市。")
        lines.append("以下为最近交易日数据。")
        lines.append("")

    data = get_stock_data()
    if data and "错误" not in data[0]:
        lines.append("【行情概览】")
        for item in data:
            lines.append(
                f"· {item['名称']}：{item['最新价']}  "
                f"涨跌幅 {item['涨跌幅']}%  "
                f"成交额 {item['成交额']}"
            )
    else:
        lines.append(f"行情获取异常：{data}")

    lines.append("")
    lines.append("⚠️ 休市提示：以上数据仅供参考，非交易日不生成完整日报。")
    lines.append("（完整六模块日报请交易日手动触发生成）")

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
    return resp

if __name__ == "__main__":
    report = build_report()
    push_to_wechat("A股行情整理", report)
