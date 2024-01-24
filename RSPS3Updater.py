#!/usr/bin/env python3

import argparse
import xml.etree.ElementTree as ET
import requests
from urllib3.exceptions import InsecureRequestWarning

import Utils
import Models
import Downloader

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


class RSPS3Updater:
    def __init__(self):
        parser = argparse.ArgumentParser(description="RSPS3Updater - Download PS3 Game Updates straight from Sony")
        parser.add_argument("-g", "--games", type=str, help="Title IDs for the PS3 games. Can be either 'BLES01807' (or comma-separated for batch downloads) or a path to a file containing one Title ID per line. Title IDs can contain dashes and parentheses")
        parser.add_argument("-d", "-p", "--downloadPath", type=str, default="./Updates", help="Path where the updates are downloaded. Defaults to './Updates'")
        parser.add_argument("-t", "--threads", type=int, default=8, help="Number of threads used for downloading. Between 1 and 32")
        args = parser.parse_args()

        self.downloadPath = Utils.check_downloads_path(args.downloadPath)
        self.gameIDs = Utils.parse_ids(args.games)
        self.numberOfThreads = Utils.validate_nr_threads(args.threads)

        self.https_session = requests.Session()
        self.https_session.mount("https://a0.ww.np.dl.playstation.net", Utils.SSLContextAdapter())

        self.downloadGamesPatches()

    def getGameMetadataXML(self, titleId):
        try:
            response = self.https_session.get(f"https://a0.ww.np.dl.playstation.net/tpl/np/{titleId}/{titleId}-ver.xml",
                                              verify=False)
            response.raise_for_status()
            if len(response.text) > 0:
                return response.text
        except requests.RequestException as e:
            print(f"Error: Failed to load game meta xml for {titleId} - {e}")

    def getGameDetails(self, titleId):
        xmlString = self.getGameMetadataXML(titleId)

        if xmlString is None:
            print(f"No patches found for {titleId}, skipping...")
            return

        xml = ET.fromstring(xmlString)
        patches = []
        gameTitle = ""

        for package in xml.iter('package'):
            patches.append(
                Models.GamePatch(
                    version=package.get('version'),
                    size=package.get('size'),
                    sha1=package.get('sha1sum'),
                    url=package.get('url')
                )
            )

            paramsfo = package.find('paramsfo')
            if paramsfo is not None:
                title = paramsfo.find('TITLE').text
                if title is not None:
                    gameTitle = Utils.filterIllegalCharsFilename(title)

        game = Models.Game(id=titleId, title=gameTitle, patches=patches)

        print(f"Found {len(game.patches)} patches for {game.id} ({game.title})")

        return game

    def downloadGamesPatches(self):
        games = []

        for gameID in self.gameIDs:
            game = self.getGameDetails(gameID)
            if game is not None:
                games.append(game)

        print(f"{len(games)} games with patches ready to be downloaded")

        for game in games:
            Downloader.GameDownloader(game=game, downloadPath=self.downloadPath,
                                      numberOfThreads=int(self.numberOfThreads / 2)).start()
