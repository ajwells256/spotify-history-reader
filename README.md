# SPOTIFY-HISTORY-READER

A simple tool to read Spotify's extended streaming history. You can follow [this guide](https://support.stats.fm/docs/import/spotify-import/) to get yours. Once you have the ZIP downloaded, you can start using this tool. [You don't even need to unzip it.](https://github.com/ajwells256/spotify-history-reader/blob/main/samples/top_artists_over_time.py#L14)


# json files contents

```json
[
    ...,
    {
        "conn_country": "SI",
        "episode_name": null,
        "episode_show_name": null,
        "incognito_mode": false,
        "ip_addr_decrypted": "1.2.3.4",
        "master_metadata_album_album_name": "Humanz",
        "master_metadata_album_artist_name": "Gorillaz",
        "master_metadata_track_name": "Andromeda (feat. DRAM)",
        "ms_played": 8778,
        "offline": false,
        "offline_timestamp": 1572964071330,
        "platform": "OS X 10.15.1 [x86 8]",
        "reason_end": "endplay",
        "reason_start": "clickrow",
        "shuffle": true,
        "skipped": null,
        "spotify_episode_uri": null,
        "spotify_track_uri": "spotify:track:2C0KFbb4v9CNWR5c9jWcKC",
        "ts": "2019-11-05T14:28:00Z",
        "user_agent_decrypted": "unknown",
        "username": "username"
    },
    ...,
]
```


## Usage

```bash
pip install -r samples/requirements.txt
python samples/top_artists_over_time.py
```

## Data Structures
See [the core class file](https://github.com/ajwells256/spotify-history-reader/blob/main/spotify_history_reader/core.py) for more details on what properties are available. Here are some key ones of interest:

### Play
The main class. An iterable of Plays is returned by the [`SpotifyHistoryReader.read()`](https://github.com/ajwells256/spotify-history-reader/blob/main/spotify_history_reader/reader.py#L49) method.

#### Members
* `artist`: The artist (or show, if episode)
* `song`: The song name (or episode name, if episode)
* `id`: The unique identifier of the song or episode. This is a Spotify URI that can be used with other Spotify APIs to read more song metadata. Samples TBD.
* `is_song`: Whether the Play is a song. If it's not a song, it's an episode.
* `timestamp`: An alias for `playback.timestamp`, the date and time at which the song was played. I think this is always UTC, and I don't belive the user's timezone is included (though the country is).

### Play.playback
Data for the playback of the track.

#### Members
* `ms_played`: Duration in milliseconds the track was played.
* `reason_start` (string)
* `reason_end` (string)
* `shuffle` (boolean)
* `skipped` (boolean)

### Play.connection
Data for the connection of the listener of the track.

#### Members
* `incognito_mode`: (boolean) Whether the user was listening with incognito mode enabled.
* `offline`: (boolean) Whether the user was offline while listening.
* `username` (string)
* `platform` (string)
* `ip` (string)
* `country` (string)