import re
import time
import requests
import json
import schedule
import datetime
from bs4 import BeautifulSoup

# Server酱配置
sckey = 'SCT276767TD9pl14Xmvh6EchYGSbPNsTcC'  # 替换为你的SCKEY

SERVER_CHAN_KEY = 'SCT276712TJnCoiKggijgh3U2bMqbz46Rd'
API_KEY = "11ecf4bbed19f6ddacdbaffd233e92a5"
CONSTELLATION_ID = 5  # 星座ID（水瓶座）

# SCT276712TJnCoiKggijgh3U2bMqbz46Rd  我
# SCT276767TD9pl14Xmvh6EchYGSbPNsTcC  包子

def get_weather(my_city):
    urls = [
        "http://www.weather.com.cn/textFC/hb.shtml",
        "http://www.weather.com.cn/textFC/db.shtml",
        "http://www.weather.com.cn/textFC/hd.shtml",
        "http://www.weather.com.cn/textFC/hz.shtml",
        "http://www.weather.com.cn/textFC/hn.shtml",
        "http://www.weather.com.cn/textFC/xb.shtml",
        "http://www.weather.com.cn/textFC/xn.shtml"
    ]
    for url in urls:
        try:
            resp = requests.get(url)
            text = resp.content.decode("utf-8")
            soup = BeautifulSoup(text, 'html5lib')
            div_conMidtab = soup.find("div", class_="conMidtab")
            if not div_conMidtab:  # 防止页面结构变化
                continue
            tables = div_conMidtab.find_all("table")
            for table in tables:
                trs = table.find_all("tr")[2:]
                for tr in trs:
                    tds = tr.find_all("td")
                    if len(tds) < 8:  # 防止索引越界
                        continue
                    city_td = tds[-8]
                    this_city = list(city_td.stripped_strings)[0]
                    if this_city == my_city:
                        high_temp = list(tds[-5].stripped_strings)[0]
                        low_temp = list(tds[-2].stripped_strings)[0]
                        weather_day = list(tds[-7].stripped_strings)[0]
                        weather_night = list(tds[-4].stripped_strings)[0]
                        wind_day = list(tds[-6].stripped_strings)
                        wind_night = list(tds[-3].stripped_strings)
                        weather_type = weather_day if weather_day != "-" else weather_night
                        wind = "".join(wind_day) if wind_day else "".join(wind_night)
                        return this_city, low_temp, high_temp, weather_type, wind
        except Exception as e:
            print(f"获取天气时出错：{str(e)}")
            continue
    # 未找到城市时返回默认值（关键修复：使用my_city而非this_city）
    return my_city, "--", "--", "--", "--"

def get_constellation(api_key, cid):
    url = "https://api.tanshuapi.com/api/constellation/v1/index"
    params = {
        "key": api_key,
        "cid": cid
    }
    try:
        response = requests.get(url, params=params)
        result = response.json()
        return result
    except Exception as e:
        print(f"查询星座失败: {e}")
        return None

def get_daily_love():
    try:
        url = "https://api.lovelive.tools/api/SweetNothings/Serialization/Json"
        res = requests.get(url, timeout=5).json()
        content = res['returnObj'][0]
        content = re.sub(r'\s+', '', content)  # 删除所有空白符

        # 微信实际最大安全长度（根据测试设为25字）


        for i in range(10):
            if(len(content) > 50):
                res = requests.get(url, timeout=5).json()
                content = res['returnObj'][0]
                content = re.sub(r'\s+', '', content)  # 删除所有空白符
            else:
                break;
        max_len = 50
        truncated = content[:max_len]
        # 零宽空格防止换行
        print(f"原始情话长度：{len(content)}，内容：{content}")  # 调试输出
        return truncated.replace(" ", "\u200B")
    except Exception as e:
        print(f"Error: {str(e)}")
        return "今天也是爱你的一天~"


def get_almanac(api_key, year, month, day):
    # API请求地址
    url = "https://api.tanshuapi.com/api/almanac/v1/index"

    # 请求参数
    params = {
        "key": api_key,
        "year": year,
        "month": month,
        "day": day
    }

    try:
        # 发送GET请求
        response = requests.get(url, params=params)
        # 解析JSON响应
        result = response.json()
        return result
    except Exception as e:
        print(f"查询失败: {e}")
        return None



def format_markdown(weather_data, almanac_data, constellation_data):
    city, tem_low, tem_high, weather_type, wind = weather_data
    today = datetime.datetime.now()
    lunar_date = almanac_data.get('solar_calendar', '--')

    # 纪念日计算
    birthday = datetime.date(2001, 7, 31)
    next_birthday = datetime.date(today.year+1, 7, 31) if today.date() > birthday.replace(year=today.year) else birthday.replace(year=today.year)
    love_days = (today.date() - datetime.date(2023, 2, 2)).days

    daylast = (today.date() - birthday ).days /36500 *100//1
    rounded_daylast = round(daylast, 1)
    print(rounded_daylast)

    # 星座数据处理
    constellation_map = {
        1: '♈白羊', 2: '♉金牛', 3: '♊双子', 4: '♋巨蟹',
        5: '♌狮子', 6: '♍处女', 7: '♎天秤', 8: '♏天蝎',
        9: '♐射手', 10: '♑摩羯', 11: '♒水瓶', 12: '♓双鱼'
    }
    content = f"""
    🌤️ **每日星语** | {today.strftime("%Y-%m-%d 星期 %w").replace("星期0", "星期日")}**  
    &ensp; &emsp; &nbsp;  
    📍 **坐标结界 ➠ {city} | 农历{lunar_date.split(' ')[-1]}  
    &ensp; &emsp; &nbsp;  
    🌦️ 实时气象站  
    ▫️ **云图** ➠ {weather_type} {get_progress_bar(85)}  
    ▫️ **温度** ➠ {tem_low}℃~{tem_high}℃ {get_progress_bar(63)}  
    ▫️ **风力** ➠ {wind} {get_progress_bar(40)}  
    &ensp; &emsp; &nbsp;  
    🔮 星座罗盘  
      {constellation_map.get(CONSTELLATION_ID, '♒')} 今日星轨解析（综合指数 {constellation_data.get('all', '--')} 分）
      &ensp; &emsp; &nbsp;  
    &ensp; &emsp; &nbsp;  
    ✨ 能量矩阵
    ➤ 健康指数：{constellation_data.get('health', '--')} 
    ➤ 爱情指数：{constellation_data.get('love', '--')}
    ➤ 工作指数：{constellation_data.get('work', '--')}
    ➤ 财运指数：{constellation_data.get('money', '--')}  
    &ensp; &emsp; &nbsp;  
    📌 幸运指南  
    - 🎰 幸运数字：{constellation_data.get('number', '--')} （今日投注概率提升20%）  
    - 🧭 贵人方位：东南方（佩戴蓝纹玛瑙有加成）  
    - ⏰ 决策时段：10:00-11:30（水星顺行窗口期）  
    ⚠️星象预警  
    &nbsp;&nbsp; &nbsp;&nbsp; &nbsp;&nbsp;{constellation_data.get('summary', '数据加载失败，请刷新重试')}   
    &ensp; &emsp; &nbsp;  
    📜 黄历解码  
    - ✨ 方位指南  
    - 🕗 喜神 : {almanac_data.get('happy_god', '--')} 
    &ensp; &emsp; &nbsp;  
    - 🕛 财神 : {almanac_data.get('wealthy_god', '--')} 
    &ensp; &emsp; &nbsp;  
    -🌟 宜行 | 
    - - {'  '.join(almanac_data.get('should', ['无数据']))[:15]} 
    -⚠️ 忌行 | 
    - - {'  '.join(almanac_data.get('avoid', ['无数据']))[:15]}
    &ensp; &emsp; &nbsp;  
    &ensp; &emsp; &nbsp;  
    💌 星缘密语  
    "{get_daily_love()}"   
    &ensp; &emsp; &nbsp;  
    📅 情话温度计：甜蜜值 {get_progress_bar(80, 5)}  
    &ensp; &emsp; &nbsp;  
    🎂 时光沙漏  
    - 🐣 破壳日誌 ➠ 第{(today.date() - birthday).days}天 {get_progress_bar(rounded_daylast)}  
    - 💘 恋爱计时 ➠ {love_days}天 ≈ {love_days // 365}年{love_days % 365 // 30}个月  
    - ⏳ 生日倒计 ➠ {(next_birthday - today.date()).days}天 | 距离♌狮子月还有{( datetime.date(2025, 7, 23) -today.date() ).days}天  
    &ensp; &emsp; &nbsp;  
    🥛 晨间密语：今日幸运早餐组合 ➠ 豆浆+粢饭团（加肉松概率提升30%）  
    &ensp; &emsp; &nbsp;  
    📍 推荐店铺：弄堂阿婆早餐铺（距您1.2km 🚴♀️8分钟可达）  
    """
    return content.strip()


def send_serverchan(msg_title, msg_content):
    url = f"https://sc.ftqq.com/{sckey}.send"
    params = {
        "text": msg_title,
        "desp": msg_content
    }
    requests.get(url, params=params)

def get_progress_bar(percentage, length=10):
    """生成可视化进度条"""
    filled = '▰' * int(percentage / 100 * length)
    empty = '▱' * (length - len(filled))
    return f"{filled}{empty} {percentage}%"

# 新增星座查询函数
def get_constellation(api_key, cid):
    url = "https://api.tanshuapi.com/api/constellation/v1/index"
    params = {"key": api_key, "cid": cid}
    try:
        response = requests.get(url, params=params, timeout=10)
        return response.json()
    except Exception as e:
        print(f"星座接口异常: {str(e)}")
        return None

def weather_report(city):
    # 获取天气数据
    weather_data = get_weather(city)

    # 获取星座数据
    constellation_data = {}
    constellation_res = get_constellation(API_KEY, CONSTELLATION_ID)
    if constellation_res and constellation_res.get("code") == 1:
        constellation_data = constellation_res['data']
    else:
        constellation_data = {
            'health': '--', 'love': '--', 'work': '--',
            'money': '--', 'number': '--', 'all': '--',
            'summary': '星座数据加载失败，建议手动刷新'
        }

    # 获取黄历数据
    today = datetime.datetime.now()
    almanac_result = get_almanac("11ecf4bbed19f6ddacdbaffd233e92a5", today.year, today.month, today.day)

    # 新增星座数据获取（假设cid=5对应目标星座）
    constellation_result = get_constellation("11ecf4bbed19f6ddacdbaffd233e92a5", 5)

    # 数据处理...
    almanac_data = almanac_result['data'] if almanac_result.get("code") == 1 else {}
    constellation_data = constellation_result['data'] if constellation_result.get("code") == 1 else {
        'health': '--',
        'love': '--',
        'work': '--',
        'money': '--',
        'number': '--',
        'all': '--',
        'summary': '--'
    }

    markdown_content = format_markdown(weather_data, almanac_data, constellation_data)
    send_serverchan(f"🌤️🥟 小包子 的每日提醒 💌 ", markdown_content)


if __name__ == '__main__':
    # 立即执行一次
    weather_report("上海")

    # 替换为你的API密钥
    api_key = "11ecf4bbed19f6ddacdbaffd233e92a5"
    # 查询日期
    today = datetime.datetime.now()
    year = today.year
    month = today.month
    day = today.day

    # 调用查询函数
    result = get_almanac(api_key, year, month, day)

    # 输出结果
    if result and result.get("code") == 1:
        print("查询成功!")
        print(f"公历日期: {result['data']['solar_calendar']}")
        print(f"农历日期: {result['data']['lunar_calendar']}")
        print(f"喜神方位: {result['data']['lucky_god']}")
        print(f"宜: {', '.join(result['data']['should'])}")
        print(f"忌: {', '.join(result['data']['avoid'])}")
    else:
        print(f"查询失败: {result.get('msg', '未知错误')}")
