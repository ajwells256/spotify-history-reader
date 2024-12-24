from collections import Counter
from matplotlib import pyplot as plt

from typing import Dict, Callable, List, Set, Tuple, Any

from spotify_history_reader import SpotifyHistoryReader, Play


def plot_top_artists_over_time(
    predicate: Callable[[Play], bool] = lambda x: True, top=5
):
    with SpotifyHistoryReader() as reader:
        reader.add_source_zip("~/Downloads/Spotify.zip")

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

    top_artists_by_year: Dict[int, Set[str]] = {
        year: set(
            map(lambda x: x[0], Counter(yearly_play_time_by_artist).most_common(top))
        )
        for year, yearly_play_time_by_artist in play_time_by_artist_by_year.items()
    }

    top_artists_over_years: Set[str] = set()
    for _, value in top_artists_by_year.items():
        top_artists_over_years = top_artists_over_years.union(value)

    plot_artists_play_data(
        top_artists_over_years,
        play_time_by_artist_by_year,
        # sort by the play time for all time
        lambda t: play_time_by_artist[t[1]],
        f"Time spent listening to all top {top} artists from each year",
    )

    ordered_years = sorted(play_time_by_artist_by_year.keys())
    for year in ordered_years:
        plot_artists_play_data(
            top_artists_by_year[year],
            play_time_by_artist_by_year,
            # sort by the play time for the current year
            lambda t: play_time_by_artist_by_year[year][t[1]],
            f"Time spent listening to top {top} artists of {year}",
        )


def plot_artists_play_data(
    artists: List[str],
    play_time_by_artist_by_year: Dict[int, Dict[str, int]],
    sort_method: Callable[
        [Tuple[Any, Any]], Any
    ],  # play_time_by_artist: Dict[str, int],
    title: str,
):
    if len(artists) == 0:
        return

    ordered_years = sorted(play_time_by_artist_by_year.keys())
    for artist in artists:
        artist_data = [
            play_time_by_artist_by_year[year].get(artist, 0) / 60000
            for year in ordered_years
        ]
        plt.plot(ordered_years, artist_data, label=artist)

    handles, labels = plt.gca().get_legend_handles_labels()

    # sort by the overall play time of the artist
    handles, labels = zip(*sorted(zip(handles, labels), key=sort_method, reverse=True))

    plt.legend(handles, labels)

    plt.xlabel("Year")
    plt.ylabel("Minutes listened")
    plt.title(title)

    plt.show()


if __name__ == "__main__":
    plot_top_artists_over_time(lambda play: play.is_song, 10)
