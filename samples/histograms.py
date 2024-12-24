from matplotlib import pyplot as plt

from typing import Dict, Callable, Any

from spotify_history_reader import SpotifyHistoryReader, Play


def hist(
    selector: Callable[[Play], Any],
    title: str,
    predicate: Callable[[Play], bool] = lambda x: True,
):
    with SpotifyHistoryReader() as reader:
        reader.add_source_zip("~/Downloads/2024_12_07_spotify.zip")

        distribution: Dict[Any, int] = {}
        for play in reader.read():
            if not predicate(play):
                continue

            value = selector(play)
            if value in distribution:
                distribution[value] += 1
            else:
                distribution[value] = 1

    keys, values = zip(*distribution.items())
    plt.bar(keys, values)
    plt.title(title)
    plt.ylabel("Songs Played")
    plt.show()


if __name__ == "__main__":
    hist(
        lambda play: play.timestamp.hour, "Hour played (UTC)", lambda play: play.is_song
    )
    hist(lambda play: play.timestamp.month, "Month played", lambda play: play.is_song)
