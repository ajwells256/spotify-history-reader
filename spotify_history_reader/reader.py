import json

from typing import List, Iterator
from spotify_history_reader.core import Play


class SpotifyHistoryReader:
    """A class for managing the reading of Plays from a set of data files."""

    def __init__(self):
        self.sources: List[str] = []

    def add_source(self, source_path: str):
        """Adds the provided source_path to the history reader."""
        self.sources.append(source_path)

    def read(self) -> Iterator[Play]:
        """Reads all the Plays in the provided source files."""
        for source_path in self.sources:
            with open(source_path, "r") as file:
                for entry in json.load(file):
                    try:
                        yield Play(**entry)
                    except:
                        print("Encountered exception while handling entry:")
                        print(entry)
                        raise
