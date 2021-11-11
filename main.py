import os
from flask import Flask, jsonify, request
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import lyricsgenius
import Levenshtein as lv

import json
import re
import tempfile
import shutil
from google.cloud import storage

import gc


sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=os.environ["SPOTIFY_client_id"],
                                                           client_secret=os.environ['SPOTIFY_client_secret'], ))


def write_file_blob(bucket_name,path, file_name, file_path):
    # Instantiate a CGS client
    client = storage.Client()

    # Retrieve all blobs with a prefix matching the folder
    bucket = client.get_bucket(bucket_name)
    # Create a new blob and upload the file's content.
    my_file = bucket.blob(f'{path}/dataset/{file_name}')
    my_file.upload_from_filename(file_path)

def remove_sqbrackets(s):
    s = s.replace('EmbedShare URLCopyEmbedCopy', '')
    # fixed the newline to save to csv correctly
    s = s.replace('\n', '\\n')
    pattern = r'\[.*?\]'
    r = re.sub(pattern, '', s)
    return r


def simple_clean(s):
    s = s.replace('EmbedShare URLCopyEmbedCopy', '')
    # fixed the newline to save to csv correctly
    s = s.replace('\n', '\\n')
    s = s.rstrip('0123456789')
    return s


def make_file_name(s):
    def remove_space_slash(st):
        st = st.replace('/', '-')
        st = st.replace(' ', '_')
        return st

    art = remove_space_slash(s.artist)
    title = remove_space_slash(s.title)
    return f'{title}-{art}.txt'


def big_fuction(user, playlist_id):
    """
    :param playlist_id:
    :return: the songs and lyrics from that playlist
    """
    pl_id = f'spotify:playlist:{playlist_id}'
    results = sp.playlist(pl_id)
    playlist_name = results['name']
    offset = 0

    playlist = []
    while True:
        response = sp.playlist_items(pl_id,
                                     offset=offset,
                                     fields='items.track.name,items.track.artists.name,total',
                                     additional_types=['track'])
        if len(response['items']) == 0:
            break

        # pprint(response['items'])
        t = response['items']
        offset = offset + len(response['items'])
        print(offset, "/", response['total'])


        for i in range(len(t)):
            song, artists = t[i]['track']['name'], t[i]['track']['artists'][0]['name']
            playlist.append({'song': song, 'artist': artists})
    print(len(playlist))

    genius = lyricsgenius.Genius(os.environ['GENIUS_SECRET'])
    genius.response_format = 'plain'
    genius.skip_non_songs = True  # Include hits thought to be non-songs (e.g. track lists)
    # genius.excluded_terms = []
    genius.verbose = False

    # if it cant find a song let the user enter a url to the song from genius
    success_list = []
    failed_list = []
    # going to have a problem when the user want to suppress the warning because im only saving the search
    warning_list_search = []
    warning_list_found = []

    for i in playlist:
        print(f'SEARCHING : {i["song"]}')

        art = genius.search_artist(i['artist'], max_songs=0)
        # No artist found
        if art == None:
            print('NO ARTIST:', i['artist'])
            failed_list.append(i)
            print('-' * 20)
            continue

        print("DEBUG:", art.name)
        song = art.song(i['song'])
        # if No results found for the song
        # try to get lyrics if cant check to remove dash -
        if song == None and '-' in i['song']:
            i['song'] = i['song'][:i['song'].index('-')]
            song = art.song(i['song'])

        # if song None and it didnt have a dash or the dash was removed failed
        if song == None:
            print("CANT FIND:", i['song'])
            failed_list.append(i)
        # song found
        else:
            # check distance
            distance = lv.distance(i['song'], song.title)

            # check for warning
            if distance >= 5:
                # check if dash in searching song and remove and recheck distance
                if '-' in i['song']:
                    i['song'] = i['song'][:i['song'].index('-')]
                    song = art.song(i['song'])
                    new_distance = lv.distance(i['song'], song.title)
                    # new check still over threshold warning
                    if new_distance >= 5:
                        print(f'WARNING LARGE DISTANCE {distance} and {new_distance}')
                        print('SONG FOUND   :', song.title)
                        warning_list_search.append(i)
                        warning_list_found.append(song)
                    # now passes
                    else:
                        print('SONG FOUND   :', song.title)
                        success_list.append(song)
                # else no dash warning
                else:
                    print(f'WARNING LARGE DISTANCE {distance}')
                    print('SONG FOUND   :', song.title)
                    warning_list_search.append(i)
                    warning_list_found.append(song)


            # no warning all good
            else:
                print('SONG FOUND   :', song.title)
                success_list.append(song)

        print('-' * 20)

    total = len(playlist)
    warns = len(warning_list_found)
    fails = len(failed_list)
    # assert success_list = total-warns-fails ;)
    print(f'Warnings: {warns}/{total}')
    print(f'Failed:{fails}/{total}')
    print(f'Success:{total - warns - fails}/{total}')

    with tempfile.TemporaryDirectory() as tmpdirname:
        print('created temporary directory', tmpdirname)
        for song in success_list:
            clean_song = simple_clean(song.lyrics)
            file_name = make_file_name(song)
            path = f'/{tmpdirname}/{file_name}'
            with open(path, 'w+') as fp:
                fp.write(clean_song)

        shutil.make_archive(f"{tmpdirname}/{playlist_name}", "zip", f"{tmpdirname}")
        print(f'{tmpdirname}/{playlist_name}')
        for x in os.listdir(tmpdirname):
            if '.zip' in x:
                print(x)
        write_file_blob('central-bucket-george', user, f'{playlist_name}.zip', f"{tmpdirname}/{playlist_name}.zip")

    gc.collect()
    return success_list


# TODO let the user choose to suppress the warning or add them to failed
'''
ans = ''
for search, found in zip(warning_list_search,warning_list_found):
  print(f'{search["song"]} , {found.title}')
  while ans.lower() != 'y' and ans.lower() != 'n':
    ans = input('is this the correct song? y/n (anything else for lyrics)')
    print(ans)
    if ans.lower() == 'y':
      success_list.append(found)
    elif ans.lower() == 'n':
      failed_list.append(search)
    else:
      print(found.lyrics)

  ans = ''
'''

# TODO fix BROKEN cant use link

# let the user add the genius url to the correct lyrics
# let the user add custom lyrics wheather it be there own or the correct lyrics from another website

'''
for fail in failed_list:
  ans = input(f'Enter a genius url for {fail["song"]} by {fail["artist"]} or nothing to skip')
  #example url https://genius.com/Johnny-cash-folsom-prison-blues-lyrics
  if ans == '':
    pass
  else:
    if 'genius.com/' in ans:
      search = ans[ans.index('genius.com/'):]
      search = search.replace('genius.com/', '')
      search = search.replace('-', ' ')
      print(search)
      song = genius.search_song(search)
      confirm = input(f'got song {song.title} by {song.artist} is this correct')
      if confirm.lower() == 'y':
        print('adding song')
        success_list.append(song)
      else:
        print('not adding')
    else:
      print(f'{ans} not a valid genius url')





print(warning_list_search)
print(failed_list)
print(len(success_list))
'''

# for now the only cleaning i do is remove everything in the square brackets.
# i have concerns about the repeating choras and interlude parts but i have to get a baseline first
# possible idea to replace all the numbers with there words
"""
pip install num2words
from num2words import num2words

# Most common usage.
print(num2words(36))
"""

'''
!pip install langdetect
from langdetect import detect
if detect(cleaner_song) != 'en':
'''

app = Flask(__name__)


@app.route("/", methods=['POST'])
def hello():
    # name = os.environ.get("NAME", "World")
    record = json.loads(request.data)
    print(record['playlist_id'])
    songs = big_fuction(record['user'], record['playlist_id'])
    out = [str(song.title) for song in songs]
    print(type(out))
    return jsonify({'found_songs': out})
    # , 'warning_songs':warning_list, 'not_found_songs':error_list})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
