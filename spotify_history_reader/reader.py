import json
import os
import zipfile
import tempfile

from typing import List, Iterator
from spotify_history_reader.core import Play


class SpotifyHistoryReader:
    """A class for managing the reading of Plays from a set of data files."""

    def __init__(self):
        self.sources: List[str] = []
        self.temp_directories: List[str] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        for temp_dir in self.temp_directories:
            for root, dirs, files in os.walk(temp_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))

    def add_source(self, source_path: str):
        """Adds the provided source_path to the history reader."""
        full_path = os.path.expanduser(source_path)
        if self._path_exists(full_path):
            self.sources.append(full_path)

    def add_source_directory(self, source_directory: str):
        """Adds all files in the provided source_directory to the history reader."""
        full_path = os.path.expanduser(source_directory)
        if self._path_exists(full_path):
            for root, _, files in os.walk(full_path):
                for file in files:
                    # TODO: Do I need to avoid non-audio files?
                    if file.endswith(".json"):
                        self.add_source(os.path.join(root, file))

    def add_source_zip(self, source_zip_path: str):
        """Adds all files in the provided source_zip_path to the history reader."""
        full_path = os.path.expanduser(source_zip_path)
        if self._path_exists(full_path):
            with zipfile.ZipFile(full_path, "r") as zip_ref:
                temp_dir = tempfile.mkdtemp()
                self.temp_directories.append(temp_dir)
                for file in zip_ref.namelist():
                    zip_ref.extract(file, temp_dir)
            self.add_source_directory(temp_dir)

    def read(self, strict=False) -> Iterator[Play]:
        """Reads all the Plays in the provided source files."""
        for source_path in self.sources:
            with open(source_path, "r") as file:
                for entry in json.load(file):
                    try:
                        yield Play(**entry)
                    except ValueError:
                        print("Encountered exception while handling entry:")
                        print(entry)
                        if strict:
                            raise
                        print("Will continue without the entry")

    def _path_exists(self, path: str) -> bool:
        if not os.path.exists(path):
            print(f"Path {path} was not found")
            return False
        return True
