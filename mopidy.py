import requests
import json
import shutil
import tempfile
import urllib.request
import threading
import time
import pygame
import traceback


class MusicPlayer(object):
    trackdata = dict()
    artist = ""
    album = ""
    title = ""
    image = None
    _imageurl = ""
    download_complete = False
    image_cache = {}
    playing = False
    muted = False
    volume = 100
    trackdata_changed = True
    old_trackimages = None
    old_trackinfo = None

    def __init__(self, hostname="127.0.0.1", port="6680", password="", shuffle=False):
        self.url = "http://"+hostname+":"+port+"/mopidy/rpc"
        if shuffle == "1":
            self.shuffle = True
        else:
            self.shuffle = False
        # print(self.checkAlarmPlaylist())
        self.update_thread = threading.Thread(target=self.updateStatus)
        self.update_thread.daemon = True
        self.update_thread.start()


    def _downloader(self):
        if self._imageurl != None and self._imageurl not in self.image_cache:
            with urllib.request.urlopen(self._imageurl) as response:
                with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                    shutil.copyfileobj(response, tmp_file)
                    self.image_cache[self._imageurl] = tmp_file.name

    def updateStatus(self):
        while True:
            self.updateTrackInfo()
            self.getState()
            self.getVolume()
            time.sleep(1)

    @property
    def imageurl(self):
        return self._imageurl

    @imageurl.setter
    def imageurl(self, url):
        if url != self._imageurl:
            self._imageurl = url
            self._downloader()
            self._t = threading.Thread(
                target=self._downloader)
            self._t.daemon = True
            self._t.start()
            self.image = pygame.Surface((1, 1), flags=pygame.SRCALPHA)
            if self._imageurl != None:
                self.image = pygame.image.load(
                    self.image_cache[self._imageurl])
                self.trackdata_changed = True

    def updateTrackInfo(self):
        artist = ""
        album = ""
        title = ""
        imagefile = ""

        try:
            trackinfo = self._clientRequest(
                "core.playback.get_current_track")["result"]
            trackimages = self._clientRequest("core.library.get_images", {
                "uris": [trackinfo["uri"]]})["result"]
            if self.old_trackinfo == trackinfo and self.old_trackimages == trackimages:
                self.trackdata_changed = False
                return
            else:
                self.old_trackinfo = trackinfo
                self.old_trackimages = trackimages
                self.trackdata_changed = True
            self.artist = trackinfo["artists"][0]["name"].strip()
            self.title = trackinfo["name"].strip()
            try:
                self.album = trackinfo["album"]["name"].strip()
            except:
                self.album = ""
            try:
                self.imageurl = trackimages[trackinfo["uri"]][0]["uri"]
            except:
                self.imageurl = None
        except Exception as e:
            print(traceback.format_exc())
            self.artist = self.album = self.title = ""
            self.imageurl = None

        if self.artist == self.album:
            self.album = ""

    def togglePlay(self):
        if self.playing:
            method = "core.playback.pause"
        else:
            method = "core.playback.play"
        self._clientRequest(method)
        self.getState()

    def play(self):
        if self.shuffle:
            method = "core.tracklist.shuffle"
            self._clientRequest(method)
        method = "core.playback.play"
        self._clientRequest(method)
        self.getState()

    def skip(self):
        self._clientRequest("core.playback.next")

    def back(self):
        self._clientRequest("core.playback.previous")

    def getVolume(self):
        try:
            self.volume = int(self._clientRequest(
                "core.playback.get_volume")["result"])
            self.muted = bool(self._clientRequest(
                "core.playback.get_mute")["result"])
        except Exception as e:
            print(e)
            self.volume = 100
            self.muted = False

    def toggleMute(self):
        self._clientRequest("core.playback.set_mute", {"mute": not self.muted})
        self.muted = bool(self._clientRequest(
            "core.playback.get_mute")["result"])

    def volup(self):
        self._clientRequest("core.playback.set_volume", {
                            "volume": self.volume + 10})
        self.getVolume()

    def voldown(self):
        self._clientRequest("core.playback.set_volume", {
                            "volume": self.volume - 10})
        self.getVolume()

    def getState(self):
        status = self._clientRequest("core.playback.get_state")["result"]
        if status == "playing":
            self.playing = True
        else:
            self.playing = False

    def setAlarmPlaylist(self):
        try:
            self.checkAlarmPlaylist()
            self._clientRequest("core.tracklist.clear")
            alarm_uri = self._clientRequest("core.playlists.filter", {
                "criteria": {"name": "Alarm"}})["result"][0]["uri"]
            alarm_tracks = self._clientRequest(
                "core.playlists.get_items", {"uri": alarm_uri})["result"]
            for track in alarm_tracks:
                self._clientRequest(
                    "core.tracklist.add", {'uri': track["uri"]})
        except Exception as e:
            print(e)

    def checkAlarmPlaylist(self):
        result = self._clientRequest("core.playlists.filter", {
            "criteria": {"name": "Alarm"}})
        if len(result["result"]) > 0:
            self.playlist = result["result"][0]["uri"]
        else:
            self.playlist = self._clientRequest("core.playlists.create", {
                "name": "Alarm"
            })["result"][0]["uri"]

    def _clientRequest(self, method, params={}):
        headers = {'content-type': 'application/json'}
        payload = {
            "method": method,
            "jsonrpc": "2.0",
            "params": params,
            "id": 1,
        }
        try:
            return requests.post(self.url, data=json.dumps(
                payload), headers=headers, timeout=1).json()

        except Exception as e:
            print(e)
            print(payload)
            return {"result": None}


if __name__ == "__main__":
    print("This module cannot be called directly.")
