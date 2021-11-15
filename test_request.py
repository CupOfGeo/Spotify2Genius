import json
import requests
from dotenv import load_dotenv
import os

load_dotenv()


URL = os.environ["URL"]
# URL = 'http://127.0.0.1:5000/'
# western cowboy 73 songs
data = {'user': 'george_test', 'playlist_id': '1bsirFMYamoch1A5GyqDkA', 'debug': True}

# 1003 song playlist https://open.spotify.com/playlist/7hDSJxfgDFNImclVNOaaEl
# data = {'user':'george', 'playlist_id':'7hDSJxfgDFNImclVNOaaEl', 'debug': True}

data_json = json.dumps(data)
r = requests.post(URL, data=data_json)
if r.status_code == 200:
    out = r.json()['found_songs']
    print(out)
else:
    print("ERROR")
