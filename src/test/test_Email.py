import os
import sys
sys.path.append('../')

from toolBox import EmailBot

os.chdir('../')
emailbot = EmailBot('../data/settings.json')
emailbot.sendOne()
