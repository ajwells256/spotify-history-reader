from collections import Counter
from os import path

from typing import Dict, Callable

from spotify_history_reader import SpotifyHistoryReader, Play


def aggregate_stats(predicate: Callable[[Play], bool] = lambda x: True, top=10):

    history_paths = [
        "/home/andrew/Downloads/2024_12_07_spotify/Spotify Extended Streaming History/Streaming_History_Audio_2017-2020_0.json",
        "/home/andrew/Downloads/2024_12_07_spotify/Spotify Extended Streaming History/Streaming_History_Audio_2020-2021_1.json",
        "/home/andrew/Downloads/2024_12_07_spotify/Spotify Extended Streaming History/Streaming_History_Audio_2021-2022_2.json",
        "/home/andrew/Downloads/2024_12_07_spotify/Spotify Extended Streaming History/Streaming_History_Audio_2022-2023_3.json",
        "/home/andrew/Downloads/2024_12_07_spotify/Spotify Extended Streaming History/Streaming_History_Audio_2023-2024_4.json",
    ]

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
    play_count_by_id: Dict[str, int] = {}
    id_name_map: Dict[str, str] = {}
    for play in reader.read():
        if not predicate(play):
            continue

        # total time
        played_ms += play.playback.ms_played

        # time by artist
        if play.artist in play_time_by_artist:
            play_time_by_artist[play.artist] += play.playback.ms_played
        else:
            play_time_by_artist[play.artist] = play.playback.ms_played

        # play count by song
        # TODO: Multiple URIs might correspond to "similar" songs, dedupe would be neat (but hard)
        if play.id in play_count_by_id:
            play_count_by_id[play.id] += 1
        else:
            id_name_map[play.id] = play.song
            play_count_by_id[play.id] = 1

    show_time_listened(played_ms)

    print(f"\nTop {top} artists by time listened")
    i = 1
    for artist, counter in Counter(play_time_by_artist).most_common(top):
        print(
            f"{str(i).ljust(3)} {artist.ljust(40)} {counter / 1000 / 60:0.0f} minutes"
        )
        i += 1

    i = 1
    print(f"\nTop {top} songs by play count")
    for play_id, counter in Counter(play_count_by_id).most_common(top):
        print(f"{str(i).ljust(3)} {id_name_map[play_id].ljust(40)} {counter} times")
        i += 1


def show_time_listened(total_ms):
    print(f"{total_ms/1000/60:0.2f} minutes")
    print(f"{total_ms/1000/60/60/24:0.2f} days")
    print(f"{total_ms/1000/60/60/24/30:0.2f} months")
    print(f"{total_ms/1000/60/60/24/365:0.2f} years")


if __name__ == "__main__":
    aggregate_stats(lambda play: play.is_song)
