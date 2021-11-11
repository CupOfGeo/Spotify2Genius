import json
import requests
URL = "0.0.0.0:8080/"
#data = {'playlist_id':'37i9dQZF1DXb3m918yXHxA'}
data = {'user':'george', 'playlist_id':'1bsirFMYamoch1A5GyqDkA'}
data_json = json.dumps(data)
r = requests.post(URL, data=data_json)
if r.status_code == 200:
    out = r.json()['found_songs']
    print(out)
else:
    print("ERROR")