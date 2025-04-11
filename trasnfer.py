from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
import spotipy
from ytmusicapi import YTMusic
import time
import random
import json
import os
import requests

#------------------------- spotify cred from spootify dev dashboard-------------------------------------------

load_dotenv()
SPOTIFY_CLIENT_ID = '73edd4323c294093a45dda1524cc3610'
SPOTIFY_CLIENT_SECRET = '7535e70f53b64cb3a6b74dec1866330a'
SPOTIFY_REDIRECT_URI = 'http://127.0.0.1:8888/callback'

session = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=3)
session.mount("https://", adapter)

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope='user-library-read playlist-read-private playlist-read-collaborative'
    ),
    requests_timeout=20,  #rate-limit
    requests_session=session
)

#-------------------------------------------------------------------------------------------------------------

#-------------------------- yt music auth from a post api request headers-------------------------------------

ytmusic = YTMusic("headers_auth.json")
print(ytmusic.get_library_playlists())

#-------------------------------------------------------------------------------------------------------------

#------------------------- transfered playlist history-------------------------------------------------------

TRANSFER_RECORD_FILE = "transferred_tracks.json"

def load_transferred_tracks():
    if os.path.exists(TRANSFER_RECORD_FILE):
        with open(TRANSFER_RECORD_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("⚠️ Warning: transfer record file is empty or corrupted. Resetting.") #empty json handling
                return {}
    return {}

def save_transferred_tracks(data):
    with open(TRANSFER_RECORD_FILE, "w") as f:
        json.dump(data, f, indent=2)

#-------------------------------------------------------------------------------------------------------------

#---------------------functions to get all playlists and their respective songs------------------------------

def get_spotify_playlists():
    playlists = []
    results = sp.current_user_playlists(limit=50)
    while results:
        playlists.extend(results['items'])
        if results['next']:
            results = sp.next(results)
        else:
            break
    return playlists

def get_tracks_from_playlist(playlist_id):
    tracks = []
    results = sp.playlist_tracks(playlist_id)
    while results:
        for item in results['items']:
            if item['track']:
                name = item['track']['name']
                artist = item['track']['artists'][0]['name']
                tracks.append({'name': name, 'artist': artist})
        if results['next']:
            results = sp.next(results)
        else:
            break
    return tracks

#----------------------------------------------------------------------------------------------------------------

#----------------------------------compare function to avoid duplication for playlists-----------------------------------------

def transfer_spotify_to_ytmusic():
    print("\n🔄 Transferring Spotify playlists to YouTube Music...")
    playlists = get_spotify_playlists()
    for playlist in playlists:
        print(f"\n🎧 Transferring playlist: {playlist['name']}")

        if playlist['name'].strip().lower() == "liked songs":
            print("⏩ Adding to YouTube's fixed Liked Songs playlist.")
            yt_playlist_id = 'YOUR_YT_MUSIC_LIKED_SONGS_PLAYLIST_ID' 
            tracks = get_tracks_from_playlist(playlist['id'])
            search_and_add_to_playlist(tracks, yt_playlist_id, playlist['name'])
            continue 

        transferred = load_transferred_tracks()
        if playlist['name'] in transferred:
            existing_yt_playlist_id = list(transferred[playlist['name']].keys())[0]
            yt_playlist_id = existing_yt_playlist_id
            print(f"⏩ Adding to existing YouTube playlist with ID: {yt_playlist_id}")
        else:
            yt_playlist_id = ytmusic.create_playlist(
                title=playlist['name'],
                description=playlist.get('description', '') or "Imported from Spotify"
            )
            print(f"🎧 Created new YouTube playlist with ID: {yt_playlist_id}")

        tracks = get_tracks_from_playlist(playlist['id'])
        search_and_add_to_playlist(tracks, yt_playlist_id, playlist['name'])
        time.sleep(random.uniform(0.5, 1.0)) 

#--------------------------------------------------------------------------------------------------
        
#-------------------------------- function to search songs and create new playlists in yt music---------------------

def search_and_add_to_playlist(tracks, yt_playlist_id, spotify_name):
    transferred = load_transferred_tracks() 

    if spotify_name not in transferred:
        transferred[spotify_name] = {}

    if yt_playlist_id not in transferred[spotify_name]:
        transferred[spotify_name][yt_playlist_id] = {'tracks': []}

    existing_tracks = transferred[spotify_name][yt_playlist_id]['tracks']

    for track in tracks:
        if any(t['name'] == track['name'] for t in existing_tracks):
            print(f"🔁 Song repeated: {track['name']} (already in playlist '{spotify_name}')")
            continue

        query = f"{track['name']} {track['artist']}"
        results = ytmusic.search(query, filter='songs')

        if results:
            video_id = results[0]['videoId']
            try:
                ytmusic.add_playlist_items(yt_playlist_id, [video_id])
                print(f"🎵 Added to playlist: {track['name']} by {track['artist']}")

                transferred[spotify_name][yt_playlist_id]['tracks'].append(track)
                save_transferred_tracks(transferred)

            except Exception as e:
                print(f"❌ Failed to add to playlist: {track['name']} - {e}")
        else:
            print(f"❌ No result for: {track['name']} by {track['artist']}")

# ------------------ Run ------------------------------------------------------------------------------------------

transfer_spotify_to_ytmusic()
