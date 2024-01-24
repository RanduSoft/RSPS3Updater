#!/usr/bin/env python3

class GamePatch:
    def __init__(self, version, size, sha1, url):
        self.version = version
        self.size = size
        self.sha1 = sha1
        self.url = url


class Game:
    def __init__(self, id, title, patches):
        self.id = id
        self.title = title
        self.patches = patches
