import json
import requests
from dotenv import load_dotenv
import os
import polling

load_dotenv()

URL = os.environ["URL"]
URL = 'http://192.168.1.201:8080/'
# western cowboy 73 songs
data = {'user': 'george_test', 'project_name': 'cowboy', 'playlist_id': '1bsirFMYamoch1A5GyqDkA', 'debug': False,
        'threshold': 5, 'num_threads': 2}


# 11 songs
# https://open.spotify.com/playlist/3PNe7PtRNZ6s1I7S0wImec
# data['playlist_id'] = '3PNe7PtRNZ6s1I7S0wImec'

# 1003 song playlist https://open.spotify.com/playlist/7hDSJxfgDFNImclVNOaaEl
# data['playlist_id'] = '7hDSJxfgDFNImclVNOaaEl'


def test_func():
    data_json = json.dumps(data)
    r = requests.post(URL, data=data_json)
    print(r)
    print(r.status_code)
    if r.status_code == 200:
        print(r.json())
        job_id = r.json()['job_id']

    else:
        print("ERROR")
        return 'FUCK'

    def check_status(response):
        print(response.json())
        if response.json()['status'] != 'Done':
            return False
        else:
            return True

    # polls every 10 second times out after 1 min
    result = polling.poll(lambda: requests.post(URL, data=json.dumps({'job_id': job_id})),
                          timeout=600,
                          step=10,
                          check_success=check_status)
    print('GOT RESULT')
    # self.last_result = result

    return result.json()


test_func()
