import json
import requests
from dotenv import load_dotenv
import os
import threading
import aiohttp
import asyncio

load_dotenv()


URL = os.environ["URL"]
URL = 'http://192.168.1.201:8080/'
# western cowboy 73 songs
data = {'user': 'george_test', 'project_name': 'cowboy', 'playlist_id': '1bsirFMYamoch1A5GyqDkA', 'debug': True}

#11 songs
# https://open.spotify.com/playlist/3PNe7PtRNZ6s1I7S0wImec
data = {'user': 'george_test', 'project_name': 'good morning', 'playlist_id': '3PNe7PtRNZ6s1I7S0wImec', 'debug': True}

# 1003 song playlist https://open.spotify.com/playlist/7hDSJxfgDFNImclVNOaaEl
data = {'user':'george', 'project_name': '1000 best songs', 'playlist_id':'7hDSJxfgDFNImclVNOaaEl', 'debug': True}



def my_threaded_func():
    data_json = json.dumps(data)
    r = requests.post(URL, data=data_json)
    print('hi')
    if r.status_code == 200:
        out = r.json()['found_songs']
        print(out)
    else:
        print("ERROR")

# thread = threading.Thread(target=my_threaded_func)
# thread.start()
# print("Spun off thread")
my_threaded_func()





# async def main():
#
#     async with aiohttp.ClientSession() as session:
#         async with session.post(URL, data=data_json) as response:
#
#             print("Status:", response.status)
#             print("Content-type:", response.headers['content-type'])
#
#             out = await response.text()
#
#
# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())
