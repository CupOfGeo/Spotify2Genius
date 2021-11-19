import threading
import time

import lyricsgenius
import Levenshtein as lv
from main import get_spotify_playlist
import os

threshold = 5
genius = lyricsgenius.Genius(os.environ['GENIUS_SECRET'], timeout=5, retries=3)
genius.response_format = 'plain'
genius.skip_non_songs = True  # Include hits thought to be non-songs (e.g. track lists)
# genius.excluded_terms = []
genius.verbose = False


def match_song(playlist: list, index: int, result: list) -> None:
    """
    What should my return type be here? dic

    then sort them into the correct lists as they come back?
    {flag : fail/warn/success , data:stuff}

    with objects as values
    {"flag": fail/warn/success, "search_song": spotify_song, "got":song_search}

    or should they have control to append to the list like they are currently doing?
    This would require locks and idk if I feel it will be worth it ill look more into it
    """
    debug = True
    found = []
    failed = []
    # TODO going to have a problem when the user want to suppress the warning because im only saving the search
    warnings = []
    for spotify_song in playlist:

        if debug:
            print(f'{index} SEARCHING : {spotify_song["song"]}')

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
                print("FOUND")
                found.append(song_search)
        else:
            if debug:
                print(f'SONG SEARCH : NONE')
            failed.append(f"{spotify_song['song']} by {spotify_song['artist']}")

        if debug:
            print('-' * 20)

    # return found, warnings, failed
    result[index] = {"found": found, "warnings": warnings, "failed": failed}


def main():
    seconds_to_sleep = 5
    playlist, playlist_name = get_spotify_playlist('7hDSJxfgDFNImclVNOaaEl')
    # 1bsirFMYamoch1A5GyqDkA COWBOY
    # Warnings: 9/76
    # Failed:8/76
    # Success:59/76
    # --- 30.43916606903076 seconds ---

    # 7hDSJxfgDFNImclVNOaaEl
    # Warnings: 142/1003
    # Failed:68/1003
    # Success:793/1003
    # --- 468.0647919178009 seconds --- 7 mins 48 seconds better than 20

    NUM_THREADS = 4
    found = []
    failed = []
    warnings = []
    debug = True

    # helper function to split lists into n chunks of similar length if not equal
    def chunk_it(seq, num):
        avg = len(seq) / float(num)
        out = []
        last = 0.0

        while last < len(seq):
            out.append(seq[int(last):int(last + avg)])
            last += avg

        return out

    part = chunk_it(playlist, NUM_THREADS)
    results = [None] * NUM_THREADS

    threads = list()
    for index in range(NUM_THREADS):
        print("Main    : create and start thread %d.", index)
        x = threading.Thread(target=match_song, args=(part[index], index, results))
        threads.append(x)
        x.start()

    for index, thread in enumerate(threads):
        thread.join()
        # thread finished add get there work and combine it back together
        found += results[index]["found"]
        warnings += results[index]["warnings"]
        failed += results[index]["failed"]

    total = len(playlist)
    warns = len(warnings)
    fails = len(failed)
    # assert success_list = total-warns-fails ;)
    if debug:
        print(f"Warnings: {warns}/{total}")
        print(f'Failed:{fails}/{total}')
        print(f'Success:{total - warns - fails}/{total}')


# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())
# loop.close()
main()
print("--- %s seconds ---" % (time.time() - start_time))
