#%%
import requests
import json

config_dict = json.load(open("../../data/pool1.json"))
print(config_dict)
url = "https://api.f2pool.com/{type}/{address}".format(
    type=config_dict["type"], address=config_dict["address"]
)
#%%

resp = requests.get(url)
print(resp.status_code, type(resp.status_code))
if resp.status_code == 200:
    data_dict = json.loads(resp.text)
    print("online number", data_dict["worker_length_online"])
