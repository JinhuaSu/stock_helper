import os
import sys

sys.path.append("../")

from toolBox import EmailBot
import time

os.chdir("../")
emailbot = EmailBot("../data/settings.json")
import requests

url = "http://hq.sinajs.cn/list=sz002739"
field_list = [
    "name",
    "open",
    "last_close",
    "price",
    "high",
    "low",
    "buy_price",
    "sell_price",
    "volume",
    "amount",
    "buy_1_volume",
    "buy_1_price",
    "buy_2_volume",
    "buy_2_price",
    "buy_3_volume",
    "buy_3_price",
    "buy_4_volume",
    "buy_4_price",
    "buy_5_volume",
    "buy_5_price",
    "sell_1_volume",
    "sell_1_price",
    "sell_2_volume",
    "sell_2_price",
    "sell_3_volume",
    "sell_3_price",
    "sell_4_volume",
    "sell_4_price",
    "sell_5_volume",
    "sell_5_price",
    "date",
    "time",
]
lower_price = 20.5


def get_price_now(url, field_list):
    resp = requests.get(url)
    print(resp.status_code, type(resp.status_code))
    if resp.status_code == 200:
        x = resp.text.split("=")[1][1:-3]
        data_dict = dict(zip(field_list, x.split(",")))
        print(data_dict)
    return float(data_dict["price"])


price_now = get_price_now(url, field_list)
while price_now > lower_price:
    time.sleep(60)
    price_now = get_price_now(url, field_list)
content = "price now is %s, lower than %s" % (price_now, lower_price)
print(content)
emailbot.sendOne({"content": content})
