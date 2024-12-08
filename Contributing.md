
# Contributing

Feel free to contribute to this project by creating issues or opening pull requests. My vision for this project is to focus on the transformation of the Spotify extended history data into python classes. How that data gets consumed I'd like to leave to the end user to decide. That being the case, I don't expect there to be much to add in terms of package features. I'd be happy to build up a library of sample consumptions of the data exposed, though.


## Development
### Building the package
```
poetry build
```

### Installing the package locally for testing
```
pip install dist/spotify_history_reader-X.Y.Z-...whl --force-reinstall --no-deps
```
