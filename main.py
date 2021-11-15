import os
from flask import Flask, jsonify, request
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import lyricsgenius
import Levenshtein as lv

import json
import re

import shutil
from google.cloud import storage

import gc
from dotenv import load_dotenv

load_dotenv()
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=os.environ["SPOTIFY_client_id"],
                                                           client_secret=os.environ['SPOTIFY_client_secret'], ))

genius = lyricsgenius.Genius(os.environ['GENIUS_SECRET'], timeout=5, retries=3)
genius.response_format = 'plain'
genius.skip_non_songs = True  # Include hits thought to be non-songs (e.g. track lists)
# genius.excluded_terms = []
genius.verbose = False


def write_file_blob(bucket_name, path, file_name, file_path):
    # Instantiate a CGS client
    client = storage.Client()

    # Retrieve all blobs with a prefix matching the folder
    bucket = client.get_bucket(bucket_name)
    # Create a new blob and upload the file's content.
    my_file = bucket.blob(f'{path}/dataset/{file_name}')
    my_file.upload_from_filename(file_path)


def clean_lyrics(s):
    # currently unused the sq_brackets with [Verse 1] are useful for generation
    # for now the only cleaning i do is remove everything in the square brackets.
    # i have concerns about the repeating chorus and interlude parts but i have to get a baseline first
    # possible idea to replace all the numbers with there words
    """
    pip install num2words
    from num2words import num2words

    # Most common usage.
    print(num2words(36))
    """

    '''
    pip install langdetect
    from langdetect import detect
    if detect(cleaner_song) != 'en':
    '''

    s = s.replace('EmbedShare URLCopyEmbedCopy', '')
    # fixed the newline to save to csv correctly
    s = s.replace('\n', '\\n')
    pattern = r'\[.*?\]'
    r = re.sub(pattern, '', s)
    return r


def simple_clean(lyrics):
    """
    removes the last line thats not song
    replaces all newline characters as these characters would be removed during tokenizing
    :param lyrics: raw lyrics
    :return: cleaner lyrics
    """
    lyrics = lyrics.replace('EmbedShare URLCopyEmbedCopy', '')
    # fixed the newline to save to csv correctly
    lyrics = lyrics.replace('\n', '\\n')
    lyrics = lyrics.rstrip('0123456789')
    return lyrics


def make_file_name(found_song):
    """
    makes a more command line friendly file name
    :param found_song:
    :return: what that file should be named
    """

    def remove_space_slash(st):
        st = st.replace('/', '-')
        st = st.replace(' ', '_')
        return st

    art = remove_space_slash(found_song.artist)
    title = remove_space_slash(found_song.title)
    return f'{title}-{art}.txt'


def get_spotify_playlist(playlist_id):
    """
    Gets all the songs from a spotify playlist from the spotify api
    :param playlist_id: spotify playlist id (the end bit of the url)
    :return: playlist, playlist_name
    """
    pl_id = f'spotify:playlist:{playlist_id}'
    results = sp.playlist(pl_id)
    playlist_name = results['name']
    offset = 0

    # getting all the songs in the spotify playlist
    playlist = []
    while True:
        response = sp.playlist_items(pl_id,
                                     offset=offset,
                                     fields='items.track.name,items.track.artists.name,total',
                                     additional_types=['track'])
        if len(response['items']) == 0:
            break

        t = response['items']
        offset = offset + len(response['items'])
        print(offset, "/", response['total'])

        for spotify_song in range(len(t)):
            song, artists = t[spotify_song]['track']['name'], t[spotify_song]['track']['artists'][0]['name']
            playlist.append({'song': song, 'artist': artists})
    print(f'{playlist_name}: {len(playlist)}')
    return playlist, playlist_name


def match_to_genius(playlist, debug=False, threshold=5):
    """
    goes throughout the spotify playlist and looks up the songs name and artist with the genius api
    a found match is a song that's within the letter distance threshold.
    a song will be flagged with a warning if something is found but outside the threshold
    a song will fail if the genius api returns None
    :param playlist: spotify_playlist
    :param debug:
    :param threshold: letter distance threshold for what should be flagged as a warning
    :return: found a list of Song Objects. warnings and failed are lists of stings with song title and author
    """
    # if it cant find a song let the user enter a url to the song from genius
    found = []
    failed = []
    # TODO going to have a problem when the user want to suppress the warning because im only saving the search
    warnings = []

    # Matching the spotify playlist songs into genius songs
    count = 0
    for spotify_song in playlist:
        count += 1
        if debug:
            print(f'{count} SEARCHING : {spotify_song["song"]}')

        song_search = genius.search_song(spotify_song['song'], spotify_song['artist'])
        if song_search is not None:
            if debug:
                print(f"SONG SEARCH : {song_search.title} {song_search.artist}")

            distance = lv.distance(spotify_song['song'], song_search.title)

            # check for warning
            if distance >= threshold:
                if debug:
                    print('WARNING')
                warnings.append(f'{song_search.title} by {song_search.artist}')

            else:
                found.append(song_search)
        else:
            print(f'SONG SEARCH : NONE')
            failed.append(f"{spotify_song['song']} by {spotify_song['artist']}")

        print('-' * 20)

    total = len(playlist)
    warns = len(warnings)
    fails = len(failed)
    # assert success_list = total-warns-fails ;)
    if debug:
        print(f"Warnings: {warns}/{total}")
        print(f'Failed:{fails}/{total}')
        print(f'Success:{total - warns - fails}/{total}')

    return found, warnings, failed


def save_lyrics_to_drive(user, found, playlist_name, bucket_name):
    """
    saves all found song lyrics to file then zip and upload to google storage bucket then delete folder and zip file
    :param bucket_name: which bucket
    :param user: user to specify which "folder" in the bucket to save it to
    :param found: songs list
    :param playlist_name: playlist name for naming folder
    :return: nothing
    """
    os.mkdir(f'{playlist_name}/')
    for song in found:
        clean_song = simple_clean(song.lyrics)
        file_name = make_file_name(song)
        path = f'{playlist_name}/{file_name}'
        with open(path, 'w+') as fp:
            fp.write(clean_song)

    shutil.make_archive(f"{playlist_name}", "zip", f"{playlist_name}")
    write_file_blob(bucket_name, user, f'{playlist_name}.zip', f"{playlist_name}.zip")
    shutil.rmtree(playlist_name)
    os.remove(f"{playlist_name}.zip")


def big_fuction(user, playlist_id, debug=False):
    """
    :param user: user needed for which bucket to save it in
    :param playlist_id:
    :param debug: print statements
    :return: the songs and lyrics from that playlist
    """

    # getting playlist from spotify
    playlist, playlist_name = get_spotify_playlist(playlist_id)

    found, warnings, failed = match_to_genius(playlist, debug)

    save_lyrics_to_drive(user, found, playlist_name, 'central-bucket-george')

    # was having some memory issues before when trying to save to TempFiles
    # which doesnt work with cloud run as it has no storage and saves everything in ram
    gc.collect()
    found_song_titles = [str(song.title) for song in found]
    return found_song_titles


# TODO let the user choose to suppress the warning or add them to failed
'''
def fix_warnings():

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
def fix_failed();

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

app = Flask(__name__)


@app.route("/", methods=['POST'])
def hello():
    # name = os.environ.get("NAME", "World")
    record = json.loads(request.data)
    print(record['playlist_id'])
    out = big_fuction(record['user'], record['playlist_id'])
    print(type(out))
    return jsonify({'found_songs': out})
    # , 'warning_songs':warning_list, 'not_found_songs':error_list})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
