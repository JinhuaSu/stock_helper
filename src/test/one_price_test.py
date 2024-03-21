import os
import sys

sys.path.append("../")

from toolBox import EmailBot
from toolBox.Ashare import *
import time

os.chdir("../")
emailbot = EmailBot("../data/settings.json")


# 止损线
lower_price = 15.7
stock_code = 'sz002739'
columns = ["open",  "close",  "high" , "low", "volume"] 
df=get_price(stock_code,frequency='1m',count=10)
price_now = df.iloc[-1,-2]
while price_now > lower_price:
    time.sleep(60)
    df=get_price(stock_code,frequency='1m',count=10)
    price_now = df.iloc[-1,-2]
content = "%s price now is %s, lower than %s" % (stock_code, price_now, lower_price)
print(content)
emailbot.sendOne({"content": content})
