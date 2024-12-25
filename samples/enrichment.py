from typing import Union, Callable, List, Set, Tuple, Any

import dotenv
import os
import json
from spotipy import Spotify, SpotifyOAuth, SpotifyException
from time import sleep
from collections import Counter
from itertools import chain

from spotify_history_reader import SpotifyHistoryReader, Play


dotenv.load_dotenv()


class Cache:
    def __init__(self, file_path):
        self.file_path = file_path
        self.cache = {}
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as file:
                self.cache = json.load(file)

    def __contains__(self, item: str):
        return item in self.cache

    def __getitem__(self, item: str):
        return self.cache[item]

    def __setitem__(self, item: str, value: Any):
        self.cache[item] = value

    def flush(self):
        dirname = os.path.dirname(self.file_path)
        os.makedirs(dirname, exist_ok=True)
        with open(self.file_path, "wt", encoding="utf-8") as file:
            json.dump(self.cache, file)


class Album:
    def __init__(self, name, release_date, total_tracks, uri):
        self.name = name
        self.release_date = release_date
        self.total_tracks = total_tracks
        self.uri = uri

    def __str__(self) -> str:
        return self.name


class Artist:
    def __init__(self, name, uri):
        self.name = name
        self.uri = uri

    def __str__(self) -> str:
        return self.name


class EnrichedTrack:
    def __init__(self, raw):
        self.raw = raw

    @property
    def album(self) -> Album:
        album_ref = self.raw["album"]
        return Album(
            album_ref["name"],
            album_ref["release_date"],
            album_ref["total_tracks"],
            album_ref["uri"],
        )

    @property
    def artists(self) -> List[Artist]:
        return [Artist(x["name"], x["uri"]) for x in self.raw["artists"]]

    @property
    def disc_number(self) -> int:
        return self.raw["disc_number"]

    @property
    def duration_ms(self) -> int:
        return self.raw["duration_ms"]

    @property
    def explicit(self) -> bool:
        return self.raw["explicit"]

    @property
    def popularity(self) -> int:
        return self.raw["popularity"]

    @property
    def track_number(self) -> int:
        return self.raw["track_number"]

    @property
    def uri(self) -> str:
        return self.raw["uri"]

    @property
    def name(self) -> str:
        return self.raw["name"]

    def __str__(self) -> str:
        return self.name


class SpotifyRepository:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        directory=".cache",
    ):
        self.artist_cache = Cache(os.path.join(directory, "artists.json"))
        self.album_cache = Cache(os.path.join(directory, "album.json"))
        self.track_cache = Cache(os.path.join(directory, "track.json"))

        self.sapi = Spotify(
            auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri="http://localhost:1234",
            )
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.artist_cache.flush()
        self.album_cache.flush()
        self.track_cache.flush()

    def _call_with_care(
        self, method: Callable[[Union[str, List[str]]], Any], arg: Union[str, List[str]]
    ):
        try:
            return method(arg)
        except SpotifyException as se:
            if se.http_status == 429:
                print(se)
                sleep(10)
                return self._call_with_care(method, arg)
        except Exception as e:
            print(e)
            raise

    def artist(self, uri: str):
        if uri not in self.artist_cache:
            self.artist_cache[uri] = self.sapi.artist(uri)
        return self.artist_cache[uri]

    def album(self, uri: str):
        if uri not in self.album_cache:
            self.album_cache[uri] = self.sapi.album(uri)
        return self.album_cache[uri]

    def track(self, uri: str) -> EnrichedTrack:
        if uri not in self.track_cache:
            self.track_cache[uri] = self.sapi.track(uri)
        return EnrichedTrack(self.track_cache[uri])

    def tracks(self, uris: List[str]) -> List[EnrichedTrack]:
        uncached_uris = [uri for uri in uris if uri not in self.track_cache]
        deduped_uris = list(set(uncached_uris))
        track_infos = []
        if len(deduped_uris) > 0:
            for i in range(0, len(deduped_uris), 50):
                if len(deduped_uris) > 5000 and i % 1000 == 0:
                    print(
                        f"{i} / {len(deduped_uris)} ({i / len(deduped_uris)} %)",
                        end="\r",
                    )
                batch_uris = deduped_uris[i : i + 50]
                if len(batch_uris) == 0:
                    break

                results = self._call_with_care(self.sapi.tracks, batch_uris)
                for track in results["tracks"]:
                    self.track_cache[track["uri"]] = track
                    track_infos.append(track)
        return [EnrichedTrack(self.track_cache[uri]) for uri in uris]


with SpotifyHistoryReader() as reader:
    reader.add_source_zip("~/Downloads/2024_12_07_spotify.zip")

    uris = []
    for play in reader.read():
        if play.is_song:
            uris.append(play.id)

client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

with SpotifyRepository(
    client_id, client_secret, "samples/.cache"
) as spotify_repository:
    enriched_tracks = spotify_repository.tracks(uris)

artists = chain.from_iterable([x.artists for x in enriched_tracks])
for artist_uri, count in Counter([x.uri for x in artists]).most_common(10):
    print(f"{artist_uri} played {count} songs")
