from datetime import datetime


class Episode:
    def __init__(self, name: str, show: str, uri: str):
        self.name: str = name
        self.show: str = show
        self.uri: str = uri

    def __repr__(self):
        return f"{self.name} ({self.show})"


class Track:
    def __init__(self, name: str, album: str, artist: str, uri: str):
        self.name: str = name
        self.album: str = album
        self.artist: str = artist
        self.uri: str = uri

    def __repr__(self):
        return f"{self.name} by {self.artist} ({self.album})"


class Connection:
    def __init__(self, data: dict):
        self.username: str = data["username"] if "username" in data else "unknown"
        self.platfrom: str = data["platfrom"] if "platfrom" in data else "unknown"
        self.ip: str = (
            data["ip_addr_decrypted"]
            if "ip_addr_decrypted" in data
            else (data["ip_addr"] if "ip_addr" in data else "unknown")
        )
        self.country: str = (
            data["conn_country"] if "conn_country" in data else "unknown"
        )
        self.offline: bool = data["offline"] if "offline" in data else False
        self.incognito_mode: bool = (
            data["incognito_mode"] if "incognito_mode" in data else False
        )


class Playback:
    def __init__(
        self,
        ms_played: int,
        reason_start: str,
        reason_end: str,
        shuffle: bool,
        skipped: bool,
        timestamp: datetime,
    ):
        self.ms_played: int = ms_played
        self.reason_start: str = reason_start
        self.reason_end: str = reason_end
        self.shuffle: bool = shuffle
        self.skipped: bool = skipped
        self.timestamp: datetime = timestamp


class Play:
    def __init__(self, **data: dict):
        self.episode: Episode = None
        self.track: Track = None

        if data["spotify_episode_uri"]:
            self.episode = Episode(
                name=data["episode_name"],
                show=data["episode_show_name"],
                uri=data["spotify_episode_uri"],
            )
        elif data["spotify_track_uri"]:
            self.track = Track(
                name=data["master_metadata_track_name"],
                album=data["master_metadata_album_album_name"],
                artist=data["master_metadata_album_artist_name"],
                uri=data["spotify_track_uri"],
            )
        else:
            raise ValueError("Invalid play")

        self.connection = Connection(data)

        self.playback = Playback(
            ms_played=data["ms_played"],
            reason_start=data["reason_start"],
            reason_end=data["reason_end"],
            shuffle=data["shuffle"],
            skipped=data["skipped"],
            timestamp=datetime.fromisoformat(data["ts"].replace("Z", "+00:00")),
        )

    @property
    def artist(self) -> str:
        """Gets the artist (or show) of the play"""
        if self.track is not None:
            return self.track.artist
        else:
            return self.episode.show

    @property
    def song(self) -> str:
        """Gets the name of the song (or the episode) of the play"""
        if self.track is not None:
            return self.track.name
        else:
            return self.episode.name

    @property
    def id(self) -> str:
        """Gets the identifier (URI) of the track played"""
        if self.track is not None:
            return self.track.uri
        else:
            return self.episode.uri

    @property
    def is_song(self) -> bool:
        """Gets whether the play was a song (the alternative being a podcast episode)"""
        return self.track is not None

    @property
    def timestamp(self) -> datetime:
        """Gets the timestamp of the play"""
        return self.playback.timestamp

    def __repr__(self):
        if self.episode:
            return str(self.episode)
        else:
            return str(self.track)
