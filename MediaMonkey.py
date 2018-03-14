import sqlite3
import os
from datetime import timedelta
import win32com.client

class MediaMonkeyRepository:
    @staticmethod
    def _iunicode_collate(s1, s2):
        string1 = s1.lower()
        string2 = s2.lower()
        if string1 == string2:
            return 0
        elif string1 < string2:
            return 1
        else:
            return -1

    def __init__(self):
        self._conn = sqlite3.connect(f'{os.environ["APPDATA"]}\\MediaMonkey\\MM.DB')
        self._conn.row_factory = sqlite3.Row
        self._conn.create_collation('IUNICODE', MediaMonkeyRepository._iunicode_collate)

    def get_album_by_id(self, id):
        c = self._conn.cursor()
        c.execute('SELECT ID, Album, Artist FROM Albums WHERE id = ?', (id,))
        return c.fetchone()

    def get_tracks_by_album_id(self, album_id):
        c = self._conn.cursor()
        c.execute('SELECT ID, Artist, DiscNumber, TrackNumber, SongTitle, IDAlbum, SongLength, Custom5 as SpotifyUri '
                  'FROM Songs '
                  'WHERE IDAlbum = ? ', (album_id,))
        return c.fetchall()

    def get_playlist_by_name(self, name):
        c = self._conn.cursor()
        c.execute('SELECT IDPlaylist, PlaylistName, IsAutoPlaylist FROM Playlists WHERE PlaylistName = ?', (name,))
        return c.fetchone()

    def get_tracks_by_playlist_id(self, playlist_id):
        c = self._conn.cursor()
        c.execute('SELECT s.ID, s.Artist, s.DiscNumber, s.TrackNumber, s.SongTitle, s.IDAlbum, s.SongLength, s.Custom5 as SpotifyUri '
                  'FROM PlaylistSongs ps '
                  'JOIN Songs s ON ps.IDSong = s.ID '
                  'WHERE ps.IDPlaylist = ? ', (playlist_id,))
        return c.fetchall()

class MediaMonkeyTrack:
    @staticmethod
    def from_row(track_row):
        track = MediaMonkeyTrack()
        track.id = track_row['ID']
        track.artist = track_row['Artist']
        track.name = track_row['SongTitle']
        track.album_id = track_row['IDAlbum'] if track_row['IDAlbum'] > 0 else None
        track.disc_number = int(track_row['DiscNumber']) if track_row['DiscNumber'] else None
        track.track_number = int(track_row['TrackNumber']) if track_row['TrackNumber'] else None
        track.length = timedelta(milliseconds=track_row['SongLength'])
        track.spotify_uri = track_row['SpotifyUri'] if track_row['SpotifyUri'] else None
        return track;

    @staticmethod
    def from_mm(track_object):
        track = MediaMonkeyTrack()
        track.id = track_object.ID
        track.artist = track_object.ArtistName
        track.name = track_object.Title
        track.album_id = track_object.Album.ID if track_object.Album.ID > 0 else None
        track.disc_number = track_object.DiscNumber
        track.track_number = track_object.TrackOrder
        track.length = timedelta(milliseconds=track_object.SongLength)
        track.spotify_uri = track_object.Custom5 if track_object.Custom5 else None
        return track;

class MediaMonkeyAlbum:
    def __init__(self, album_row, track_rows):
        self.id = album_row['ID']
        self.name = album_row['Album']
        self.artist = album_row['Artist']
        self.tracks = []
        for track_row in track_rows:
            self.tracks.append(MediaMonkeyTrack.from_row(track_row))

class MediaMonkey:
    def __init__(self):
        self._repo = MediaMonkeyRepository()
        self._mm = None

    def _get_mm(self):
        if not self._mm:
            self._mm = win32com.client.Dispatch("SongsDB.SDBApplication")
            self._mm.ShutdownAfterDisconnect = True
        return self._mm

    def get_unlinked_albums_from_playlist(self, playlist_name):
        returned_album_ids = set()
        for track in self.get_playlist_tracks(playlist_name):
            if track.spotify_uri == None and track.album_id != None and not track.album_id in returned_album_ids:
                returned_album_ids.add(track.album_id)
                yield self.get_album_by_id(track.album_id)

    def get_unlinked_tracks_from_playlist(self, playlist_name):
        for track in self.get_playlist_tracks(playlist_name):
            if track.spotify_uri == None:
                yield track

    def get_album_by_id(self, album_id):
        album_row = self._repo.get_album_by_id(album_id)
        track_rows = self._repo.get_tracks_by_album_id(album_id)
        return MediaMonkeyAlbum(album_row, track_rows)

    def get_playlist_tracks(self, playlist_name):
        playlist_row = self._repo.get_playlist_by_name(playlist_name)
        if playlist_row['IsAutoPlaylist'] == 1:
            mm = self._get_mm()
            for track_object in mm.PlaylistByTitle(playlist_name).Tracks:
                if track_object == None:
                    return
                yield MediaMonkeyTrack.from_mm(track_object)

        for track_row in self._repo.get_tracks_by_playlist_id(playlist_row['IDPlaylist']):
            yield MediaMonkeyTrack.from_row(track_row)

    def update_track_spotify_uris(self, track_id_spotify_uri_list):
        mm = self._get_mm()
        for track_id_spotify_uri in track_id_spotify_uri_list:
            iterator = mm.Database.QuerySongs(f'AND Songs.ID = {track_id_spotify_uri[0]}')
            if iterator.EOF:
                raise Exception(f'Cannot find song with ID {track_id_spotify_uri[0]}')
            song = iterator.Item
            song.Custom5 = track_id_spotify_uri[1]
            song.UpdateDB()
