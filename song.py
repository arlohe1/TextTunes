import datetime

# this class is used to store pertinent data for a given song on Spotify
class Song:
    def __init__(self, name, artist, preview_url, uri):
        self.name = name
        self.artist = artist
        self.preview_url = preview_url
        self.uri = uri
        self.time = datetime.datetime.now()

    def get_name(self):
        return self.name

    def get_artist(self):
        return self.artist

    def get_url(self):
        return self.preview_url

    def get_uri(self):
        return self.uri

    def get_time(self):
        return self.time