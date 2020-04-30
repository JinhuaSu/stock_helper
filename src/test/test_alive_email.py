import os
import sys
sys.path.append('../')

from toolBox import EmailBot,get_one_data

os.chdir('../')
emailbot = EmailBot('../data/settings.json')
data = get_one_data('sh600258')
emailbot.sendOne({'title':'首旅酒店当前行情','content':str(data)})