import requests

def get_one_data(stock_code):
    url = "http://hq.sinajs.cn/list=%s" % stock_code
    field_list =['name','open','last_close','price','high','low','buy_price','sell_price','volume','amount','buy_1_volume','buy_1_price','buy_2_volume','buy_2_price','buy_3_volume','buy_3_price','buy_4_volume','buy_4_price','buy_5_volume','buy_5_price','sell_1_volume','sell_1_price','sell_2_volume','sell_2_price','sell_3_volume','sell_3_price','sell_4_volume','sell_4_price','sell_5_volume','sell_5_price','date','time']
    resp = requests.get(url)
    print(resp.status_code,type(resp.status_code))
    if resp.status_code == 200:
        x = resp.text.split('=')[1][1:-3]
        data_dict = dict(zip(field_list,x.split(',')))
        return data_dict
    else:
        return None