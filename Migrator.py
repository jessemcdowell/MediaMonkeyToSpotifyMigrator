import Spotify
import Matching
import MediaMonkey

spotify = Spotify.Spotify()
media_monkey = MediaMonkey.MediaMonkey()

def find_match_for_album(local_album):
    if not local_album.name:
        return None
    search_results = list(spotify.search_album(local_album.name + ' ' + local_album.artist))
    if len(search_results) == 0:
        search_results = list(spotify.search_album(local_album.name))
    return Matching.best_match(search_results, [
        Matching.text_matcher(lambda input: input.name, local_album.name, 100),
        Matching.text_matcher(lambda input: input.first_artist, local_album.artist, 50)
        ], 100)

def find_track_matches_for_album_tracks(local_album):
    album = find_match_for_album(local_album)
    if album:
        album_tracks = list(spotify.get_album_tracks(album.spotify_uri))
        for local_track in local_album.tracks:
            if not local_track.spotify_uri:
                best_match = Matching.best_match(album_tracks, [
                    Matching.text_matcher(lambda input: input.name, local_track.name, 100),
                    Matching.text_matcher(lambda input: input.artists, local_track.artist, 100),
                    Matching.text_matcher(lambda input: input.first_artist, local_track.artist, 50),
                    Matching.boolean_matcher(lambda input: local_track.track_number and input.track_number == local_track.track_number, 50),
                    Matching.boolean_matcher(lambda input: local_track.track_number and input.track_number != local_track.track_number, -100),
                    Matching.boolean_matcher(lambda input: input.disc_number or 1 == local_track.disc_number, 10),
                    Matching.boolean_matcher(lambda input: abs(input.length - local_track.length).total_seconds() < 2, 80),
                    Matching.boolean_matcher(lambda input: abs(input.length - local_track.length).total_seconds() < 5, 20)
                    ], 200)
                if best_match:
                    yield (local_track,best_match)

def find_match_for_track(local_track):
    search_results = list(spotify.search_track(f'{local_track.name} {local_track.artist}'))
    return Matching.best_match(search_results, [
        Matching.text_matcher(lambda input: input.name, local_track.name, 100),
        Matching.text_matcher(lambda input: input.artists, local_track.artist, 100),
        Matching.text_matcher(lambda input: input.first_artist, local_track.artist, 50),
        Matching.boolean_matcher(lambda input: abs(input.length - local_track.length).total_seconds() < 2, 80),
        Matching.boolean_matcher(lambda input: abs(input.length - local_track.length).total_seconds() < 5, 20)
        ], 180)

def link_tracks_from_playlist(playlist_name):
    unlinked_local_albums = media_monkey.get_unlinked_albums_from_playlist(playlist_name)
    for local_album in unlinked_local_albums:
        matches = find_track_matches_for_album_tracks(local_album)
        media_monkey.update_track_spotify_uris((m[0].id,m[1].spotify_uri) for m in matches)
    unlinked_local_tracks = media_monkey.get_unlinked_tracks_from_playlist(playlist_name)
    for local_track in unlinked_local_tracks:
        remote_track = find_match_for_track(local_track)
        if remote_track != None:
            media_monkey.update_track_spotify_uris([(local_track.id,remote_track.spotify_uri)])

def create_playlist_from_local(playlist_name):
    tracks = list(media_monkey.get_playlist_tracks(playlist_name))
    if not any(track.spotify_uri for track in tracks):
        raise Exception(f'Playlist {playlist_name} has no linked tracks!')
    spotify.create_playlist(playlist_name, (track.spotify_uri for track in tracks if track.spotify_uri))
