#!/usr/bin/env python3

import hashlib
import shutil
import requests
import threading
import os
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


class PatchDownloader:
    def __init__(self, patch, num_threads, output_dir, output_filename, proxies=None):
        self.patch = patch
        self.num_threads = num_threads
        self.output_dir = output_dir
        self.output_filename = output_filename
        self.proxies = proxies
        self.session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))

    def start(self):
        attempts = 3
        for attempt in range(attempts):
            try:
                self.download()
                if self.validate_file():
                    break
                else:
                    os.remove(os.path.join(self.output_dir, self.output_filename))
                    print("Hash validation failed, retrying...")
            except Exception as e:
                print(f"Error: Failed to download file -- {e}")

    def download(self):
        with self.session.get(self.patch.url, stream=True, proxies=self.proxies) as r:
            r.raise_for_status()

        part_size = int(self.patch.size) // self.num_threads
        threads = []

        for i in range(self.num_threads):
            start = i * part_size
            end = None if i == self.num_threads - 1 else start + part_size - 1

            thread = threading.Thread(target=self.download_part, args=(i, start, end))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        self.combine_parts()

    def download_part(self, part_num, start, end):
        part_path = os.path.join(self.output_dir, f'{self.output_filename}_part_{part_num}')
        range_header = f'bytes={start}-' if end is None else f'bytes={start}-{end}'
        headers = {'Range': range_header}

        with self.session.get(self.patch.url, headers=headers, stream=True, proxies=self.proxies) as r:
            r.raise_for_status()
            with open(part_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=32768):
                    if chunk:
                        f.write(chunk)

    def combine_parts(self):
        final_path = os.path.join(self.output_dir, self.output_filename)
        with open(final_path, 'wb') as final_file:
            for i in range(self.num_threads):
                part_path = os.path.join(self.output_dir, f'{self.output_filename}_part_{i}')
                with open(part_path, 'rb') as part_file:
                    shutil.copyfileobj(part_file, final_file)
                os.remove(part_path)

    def validate_file(self):
        final_path = os.path.join(self.output_dir, self.output_filename)

        with open(final_path, "rb") as f:
            fhash = f.read()[-32:].hex()[:40]
        # copy file
        f2 = f"{final_path}.sha1"
        shutil.copy(final_path, f2)
        # remove last 32 bytes because the PKG hash is at EOF and not part of the PKG data
        with open(f2, "ab") as f:
            f.seek(-32, os.SEEK_END)
            f.truncate()
        # calculate hash from file - last 32 bytes
        sha1 = hashlib.sha1()
        with open(f2, "rb") as f:
            for line in iter(lambda: f.read(sha1.block_size), b''):
                sha1.update(line)
        os.remove(f2)

        if fhash == sha1.hexdigest():
            return sha1.hexdigest() == self.patch.sha1
        else:
            return False


class GameDownloader:
    def __init__(self, game, downloadPath, numberOfThreads):
        self.game = game
        self.downloadPath = downloadPath
        self.numberOfThreads = numberOfThreads

    def start(self):
        print(f"Will download {len(self.game.patches)} patches for {self.game.id} ({self.game.title})...")

        patchesFolder = f"{self.game.title} [{self.game.id}]"
        patchesFolderPath = os.path.join(self.downloadPath, patchesFolder)

        if not os.path.exists(patchesFolderPath):
            os.makedirs(patchesFolderPath)

        threads = []
        for patch in self.game.patches:
            thread = threading.Thread(target=self.downloadPatch, args=(patch, patchesFolderPath, patchesFolder))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        print(f"Finished downloading all {len(self.game.patches)} patches for {self.game.id} ({self.game.title})")

    def downloadPatch(self, patch, patchesFolderPath, patchesFolder):
        patchFileName = f"{patchesFolder} v{patch.version}.pkg"
        PatchDownloader(patch=patch, num_threads=self.numberOfThreads, output_dir=patchesFolderPath, output_filename=patchFileName).start()
        print(f"Download finished: {patchFileName}")
