from spotify_history_reader.reader import SpotifyHistoryReader


def test_can_instantiate():
    with SpotifyHistoryReader() as reader:
        assert True
