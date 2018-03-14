# MediaMonkeyToSpotifyMigrator
A tool for migrating MediaMonkey playlists to Spotify

# How it works

The migration of playlists works in two stages:
1. Find matches for local tracks in Spotify
2. Create a playlist with the tracks

When tracks are matched with Spotify, the Spotify URI is saved in the Custom5 field for the track in Media Monkey. Doing so allows you to inspect the matches it made, and match tracks manually where the migrator was unable to do so. Of course, this also means that you cannot have any values in Custom5 field, or the system will not work.

# Usage

1. Make a copy of the file `SpotifyCredentials.example.py` called `SpotifyCredentials.py`
1. Register an application with Spotify, and enter the credentials in the file
1. Install [Python](https://www.python.org/) 3.6 or newer.
1. Run python, and enter the following:
````
import Migrator
Migrator.link_tracks_from_playlist('PLAYLIST NAME')
Migrator.create_playlist_from_local('PLAYLIST NAME')
````
   * The first time you run this, a browser will open so that you can log into Spotify. Once you log in, you'll be redirected to a page on localhost that should fail. Copy the full URL, and paste into the console window.
   * You may want to inspect the matching of your tracks before running the last step.

# License

See: [LICENSE](LICENSE)