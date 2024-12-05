from collections import Counter
from os import path

from typing import Dict

from src.reader import SpotifyHistoryReader


def aggregate_stats(year: int = None, top=10):

    history_paths = ["data/example.json"]

    reader = SpotifyHistoryReader()
    for history_path in history_paths:
        if not path.exists(history_path):
            print(
                "Ensure to update this sample to include one or more real spotify streaming history files"
            )
            exit(-1)
        reader.add_source(history_path)

    played_ms = 0
    play_time_by_artist: Dict[str, int] = {}
    play_count_by_song: Dict[str, int] = {}
    for play in reader.read():
        if year is not None and play.playback.timestamp.year != year:
            continue

        # total time
        played_ms += play.playback.ms_played

        # time by artist
        if play.artist in play_time_by_artist:
            play_time_by_artist[play.artist] += play.playback.ms_played
        else:
            play_time_by_artist[play.artist] = play.playback.ms_played

        # play count by song
        # TODO: Songs that share names will overlap. I wonder if there's a unique identifier for tracks I could use instead
        if play.song in play_count_by_song:
            play_count_by_song[play.song] += 1
        else:
            play_count_by_song[play.song] = 1

    show_time_listened(played_ms)

    print(f"Top {top} artists by time listened")
    i = 1
    for artist, counter in Counter(play_time_by_artist).most_common(top):
        print(f"{i} {artist.ljust(20)} {counter / 1000 / 60:0.0f} minutes")
        i += 1

    print(f"Top {top} songs by play count")
    for song, counter in Counter(play_count_by_song).most_common(top):
        print(f"{i} {song.ljust(20)} {counter} times")
        i += 1


def show_time_listened(total_ms):
    print(f"{total_ms/1000:0.2f} seconds")
    print(f"{total_ms/1000/60:0.2f} minutes")
    print(f"{total_ms/1000/60/60:0.2f} hours")
    print(f"{total_ms/1000/60/60/24:0.2f} days")
    print(f"{total_ms/1000/60/60/24/30:0.2f} months")
    print(f"{total_ms/1000/60/60/24/365:0.2f} years")


if __name__ == "__main__":
    aggregate_stats()
