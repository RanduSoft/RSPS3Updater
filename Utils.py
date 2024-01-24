#!/usr/bin/env python3

import re
import sys
import ssl
import requests
import os
import platform
from requests.adapters import HTTPAdapter


class SSLContextAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        kwargs['ssl_context'] = context
        return super(SSLContextAdapter, self).init_poolmanager(*args, **kwargs)


def validate_nr_threads(threads):
    if 1 <= threads <= 32:
        return threads
    else:
        print(f"Error: {threads} is not a valid number of threads. It must be between 1 and 32")
        sys.exit(1)


def clean_id(raw_id):
    cleaned_id = re.sub(r'[\-\(\)]', '', raw_id)
    if re.match(r'^B[A-Z]{3}\d{5}$', cleaned_id):
        return cleaned_id
    else:
        return None


def parse_ids_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        return [clean_id(line.strip()) for line in lines if clean_id(line.strip())]


def check_downloads_path(downloadArg):
    if not os.path.isdir(downloadArg):
        if not os.path.dirname(downloadArg):
            print(f"Error: {downloadArg} is not a valid download path")
            sys.exit(1)
        else:
            try:
                os.makedirs(downloadArg, exist_ok=True)
                return downloadArg
            except OSError as error:
                print(f"Error creating directory '{downloadArg}': {error}")
                sys.exit(1)
    else:
        return downloadArg


def parse_ids(gamesArg):
    if gamesArg is None:
        print("You must specify title IDs or a path to a file with title IDs in the -g or --games argument")
        sys.exit(1)

    ids = []
    if os.path.isfile(gamesArg):
        # Read title ids from file
        ids = parse_ids_from_file(gamesArg)
    else:
        if "," in gamesArg:
            # Read the array delimited by string
            ids = [clean_id(id.strip()) for id in gamesArg.split(',') if clean_id(id.strip())]
        else:
            # Try reading one title id
            single_id = clean_id(gamesArg.strip())
            if single_id:
                ids = [single_id]

    if not ids:
        print("Failed to find any valid PS3 Title ID")
        sys.exit(1)

    print(f"Found {len(ids)} valid PS3 Title IDs: {ids}")

    return ids

def massReplace(find, replace, stri):
    out = stri
    for item in find:
        out = out.replace(item, replace)
    return out

def filterIllegalCharsFilename(path):
    if platform.system() == "Windows":
        return massReplace([":","/","\\","*","?","<",">","\"","|","™","®"], "", path)
    elif platform.system() == "Linux":
        return massReplace(["/", "\x00"], "", path)
    elif platform.system() == "Darwin":
        return massReplace(["/", "\x00", ":"], "", path)

