from collections import Counter
from matplotlib import pyplot as plt

from typing import Dict, Callable, Set

from spotify_history_reader import SpotifyHistoryReader, Play


def plot_top_artists_over_time(
    predicate: Callable[[Play], bool] = lambda x: True, top=5
):
    with SpotifyHistoryReader() as reader:
        reader.add_source_zip("/home/andrew/Downloads/2024_12_07_spotify.zip")

        play_time_by_artist: Dict[str, int] = {}
        play_time_by_artist_by_year: Dict[int, Dict[str, int]] = {}
        for play in reader.read():
            if not predicate(play):
                continue

            # time by artist:
            if play.artist not in play_time_by_artist:
                play_time_by_artist[play.artist] = play.playback.ms_played
            else:
                play_time_by_artist[play.artist] += play.playback.ms_played

            # time by artist by year
            if play.timestamp.year not in play_time_by_artist_by_year:
                play_time_by_artist_by_year[play.timestamp.year] = {}

            if play.artist in play_time_by_artist_by_year[play.timestamp.year]:
                play_time_by_artist_by_year[play.timestamp.year][
                    play.artist
                ] += play.playback.ms_played
            else:
                play_time_by_artist_by_year[play.timestamp.year][
                    play.artist
                ] = play.playback.ms_played

    ordered_years = sorted(play_time_by_artist_by_year.keys())
    top_artists_over_years: Set[str] = set()
    for year in ordered_years:
        top_artists_over_years = top_artists_over_years.union(
            [
                key
                for key, _ in Counter(play_time_by_artist_by_year[year]).most_common(
                    top
                )
            ]
        )

    for artist in top_artists_over_years:
        artist_data = [
            play_time_by_artist_by_year[year].get(artist, 0) / 60000
            for year in ordered_years
        ]
        plt.plot(ordered_years, artist_data, label=artist)

    handles, labels = plt.gca().get_legend_handles_labels()

    # sort by the overall play time of the artist
    handles, labels = zip(
        *sorted(
            zip(handles, labels), key=lambda t: play_time_by_artist[t[1]], reverse=True
        )
    )

    plt.legend(handles, labels)

    plt.xlabel("Year")
    plt.ylabel("Minutes listened")

    plt.show()


if __name__ == "__main__":
    plot_top_artists_over_time(lambda play: play.is_song)
