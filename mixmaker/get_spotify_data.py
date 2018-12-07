#!/usr/bin/env python3
import spotify_scraper
import database_interaction

ss = spotify_scraper.SpotifyScraper()
db = database_interaction.DatabaseInteraction()

def get_artist(artist_id=None, artist_name=None):
    if artist_name is None:
        artist = db.get_next_artist_for_spotify()
        artist_name = artist['name']
    tracks = ss.search_artist_get_tracks(artist['name'])
