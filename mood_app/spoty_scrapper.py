# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 15:56:17 2024

@author: pc
"""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import time
import numpy as np

# Spotify credentials
client_id= "c072b2d4abd840a6add05e568c9b37c0"
client_secret= "39c4cde3bc0a4bada6c2afa77232efbd"


# Authenticate with Spotify API
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Function to retrieve audio features for a track
def get_track_audio_features(track_uri):
    features = sp.audio_features(track_uri)[0]
    return {
        "danceability": features["danceability"],
        "acousticness": features["acousticness"],
        "energy": features["energy"],
        "instrumentalness": features["instrumentalness"],
        "liveness": features["liveness"],
        "valence": features["valence"],
        "loudness": features["loudness"],
        "speechiness": features["speechiness"],
        "tempo": features["tempo"]
    }

# Function to retrieve information about an album
def get_album_info(album_uri):
    album_info = sp.album(album_uri)
    return {
        "album": album_info["name"]
    }

# Function to retrieve information about tracks in an album
def get_tracks_info(item_uri, item_type):
    tracks = []
    if item_type == "album":
        tracks_info = sp.album_tracks(item_uri)
    elif item_type == "playlist":
        tracks_info = sp.playlist_tracks(item_uri)
    for track in tracks_info["items"]:
        if item_type == "playlist":
            track = track["track"]
        track_features = get_track_audio_features(track["uri"])
        track_info = {
            "name": track["name"],
            "id": track["id"],
            **track_features
        }
        tracks.append(track_info)
    return tracks


# Function to retrieve all albums and their tracks for a given artist
def get_tracks(item_name):
    tracks = []
    # Check if item_name is an artist name or a playlist link
    if "open.spotify.com/playlist/" in item_name:
        playlist_id = item_name.split("playlist/")[-1].split("?")[0]
        playlist_info = sp.playlist(playlist_id)
        playlist_tracks = get_tracks_info(playlist_id, "playlist")
        for track in playlist_tracks:
            track["artist"] = playlist_info["owner"]["display_name"]
            track["album"] = playlist_info["name"]
        tracks.extend(playlist_tracks)
    else:
        artist_info = sp.search(item_name, type="artist")["artists"]["items"][0]
        artist_albums = sp.artist_albums(artist_info["uri"], album_type="album")["items"]
        for album in artist_albums:
            album_info = get_album_info(album["uri"])
            album_tracks = get_tracks_info(album["uri"],"album")
            for track in album_tracks:
                track["artist"] = item_name
                track["album"] = album_info["album"]
            tracks.extend(album_tracks)
    return tracks

# Main function to retrieve and compile data
def main(user_input):
    all_tracks = get_tracks(user_input)
    df = pd.DataFrame(all_tracks)
    # Reorder columns
    df = df[["name", "artist", "album", "id", "danceability", "acousticness", "energy", "instrumentalness", "liveness", "valence", "loudness", "speechiness", "tempo"]]
    json_output = df.to_json(orient='records')
    
    return json_output


