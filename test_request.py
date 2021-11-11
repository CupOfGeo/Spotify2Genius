import json
import requests
URL = "https://spotify2genius-2bzqm6tl4q-ue.a.run.app/"
#data = {'playlist_id':'37i9dQZF1DXb3m918yXHxA'}
data = {'user':'george', 'playlist_id':'1bsirFMYamoch1A5GyqDkA'}
data_json = json.dumps(data)
r = requests.post(URL, data=data_json)
if r.status_code == 200:
    out = r.json()['found_songs']
    print(out)
else:
    print("ERROR")