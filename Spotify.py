import spotipy
import spotipy.util as spotipy_util
import SpotifyCredentials
from datetime import timedelta

class SpotifyItem:
    def __init__(self, data):
        self.name = data['name']
        self.spotify_uri = data['uri']
        self.first_artist = data['artists'][0]['name']
        self.artists = '; '.join(artist['name'] for artist in data['artists'])

class SpotifyAlbumInfo(SpotifyItem):
    def __init__(self, data):
        SpotifyItem.__init__(self, data)

class SpotifyTrackInfo(SpotifyItem):
    def __init__(self, data):
        SpotifyItem.__init__(self, data)
        self.disc_number = data['disc_number']
        self.track_number = data['track_number']
        self.length = timedelta(milliseconds=data['duration_ms'])

class Spotify:
    def __init__(self):
        self._token = spotipy_util.prompt_for_user_token('',
            scope='user-library-read user-read-private playlist-modify-private',
            client_id=SpotifyCredentials.client_id,
            client_secret=SpotifyCredentials.client_secret,
            redirect_uri='http://localhost/')
        self._client = spotipy.Spotify(self._token)
        self._user = self._client.current_user()
        self._user_id = self._user['id']
        self._market = 'from_token'

    def search_album(self, query):
        response = self._client.search(q=query, type='album', market=self._market)
        for item in response['albums']['items']:
            yield SpotifyAlbumInfo(item)

    def search_track(self, query):
        response = self._client.search(q=query, type='track', market=self._market)
        for item in response['tracks']['items']:
            yield SpotifyTrackInfo(item)

    def get_album_tracks(self, spotify_uri):
        response = self._client.album_tracks(spotify_uri)
        while response:
            for item in response['items']:
                yield SpotifyTrackInfo(item)
            if response['next']:
                response = self._client.next(response)
            else:
                response = None

    def create_playlist(self, playlist_name, track_uris):
        playlist = self._client.user_playlist_create(self._user_id, playlist_name, public=False)
        id_list = list(track_uris)
        max_items_per_call = 100
        for i in range(0, len(id_list), max_items_per_call):
            self._client.user_playlist_add_tracks(self._user_id, playlist['id'], id_list[i:i+max_items_per_call])
