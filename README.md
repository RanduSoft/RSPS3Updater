# RSPS3Updater
### Download PS3 Game Updates straight from Sony

This is a simple python CLI app to download PS3 game updates at the highest speed and convinience. It was build so I could complete my offline collection of patches considering that the PS3 PSN will go down soon.

## Installation
You need Python and `requests` installed to run this CLI app.

With python and PIP installed:
```
python -m pip install requests
```

## Usage
Run `python main.py -h` to get the latest help

```
options:
  -h, --help            show this help message and exit
  -g GAMES, --games GAMES
                        Title IDs for the PS3 games. Can be either 'BLES01807' (or comma-separated for batch
                        downloads) or a path to a file containing one Title ID per line. Title IDs can contain dashes
                        and parentheses
  -d DOWNLOADPATH, -p DOWNLOADPATH, --downloadPath DOWNLOADPATH
                        Path where the updates are downloaded. Defaults to './Updates'
  -t THREADS, --threads THREADS
                        Number of threads used for downloading. Between 1 and 32
```

You can also use the binaries available [here](https://github.com/rursache/RSPS3Updater/releases/latest)

## Example
```
RSPS3Updater.exe -g ids -d Updates -t 8
```
This will download all the updates for the game ids inside the `ids` file and save the `.pkg` files inside a `Updates` directory. Downloading will be done on `8 threads`

## Building
Install and use `pyinstaller` to obtain a binary:
```
pyinstaller --onefile main.py
```

## Thanks
Thanks to [shinrax2](https://github.com/shinrax2) for his [PS3GameUpdateDownloader](https://github.com/shinrax2/PS3GameUpdateDownloader) that inspired me to create something faster and better for my needs
