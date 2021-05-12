# 2. Изучить список открытых API (https://www.programmableweb.com/category/all/apis).
# Найти среди них любое, требующее авторизацию (любого типа). Выполнить запросы к нему, пройдя авторизацию.
# Ответ сервера записать в файл.
# https://developers.google.com/youtube/v3/sample_requests

import requests
import json
from utils import f_path

api_key = 'AIzaSyCjNCn7GGRwr_3ugg9fzwcQMZ8ZQA-3XI0'
channel_id = 'UC8QMvQrV1bsK7WO37QpSxSg'

url = 'https://youtube.googleapis.com/youtube/v3/subscriptions'

params = {'key': api_key, 'part': 'snippet,contentDetails', 'channelId': channel_id}
resp = requests.get(url, params=params).json()

with open(f'{f_path}youtube_subscriptions.json', 'w') as f:
    f.write(json.dumps(resp, indent=4, sort_keys=True))
