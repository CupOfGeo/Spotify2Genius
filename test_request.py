import json
import requests
from dotenv import load_dotenv

load_dotenv()

URL = "https://spotify2genius-2bzqm6tl4q-ue.a.run.app/"
URL = 'http://127.0.0.1:5000/'
data = {'user': 'george2', 'playlist_id': '1bsirFMYamoch1A5GyqDkA', 'debug': True}
# 1003 song playlist https://open.spotify.com/playlist/7hDSJxfgDFNImclVNOaaEl
# data = {'user':'george', 'playlist_id':'7hDSJxfgDFNImclVNOaaEl', 'debug': True}
data_json = json.dumps(data)
r = requests.post(URL, data=data_json)
if r.status_code == 200:
    out = r.json()['found_songs']
    print(out)
else:
    print("ERROR")
