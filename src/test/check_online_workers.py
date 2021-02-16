#%%
import requests
import json
import time
import os
import sys


sys.path.append("../")
from toolBox import EmailBot

os.chdir("../")
emailbot = EmailBot("../data/settings.json")

config_path_list = ["../data/pool1.json", "../data/pool2.json"]

count = 0
flag = 0
while True:
    time.sleep(1)
    count += 1
    for config_path in config_path_list:
        config_dict = json.load(open(config_path))
        if count % config_dict["check_per_seconds"] == 0:
            url = "https://api.f2pool.com/{type}/{address}".format(
                type=config_dict["type"], address=config_dict["address"]
            )
            resp = requests.get(url)
            if resp.status_code == 200:
                data_dict = json.loads(resp.text)
                if data_dict["worker_length_online"] < config_dict["number"]:
                    flag += 1
                    content = (
                        "pool for {type} has some bot offline pleace check".format(
                            config_dict["type"]
                        )
                    )
                    emailbot.sendOne({"content": content})
    if flag >= 6:
        break
