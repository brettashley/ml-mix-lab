#!/usr/bin/env python3

import selenium
from selenium.webdriver import Firefox, Chrome
import time
from scraper import Scraper
from DatabaseInteraction import DatabaseInteraction

url_soul_funk_disco = 'https://www.whosampled.com/genre/Soul-Funk-Disco/'

def main(url=None, get_genre=True, get_first_artist_songs=True, artists_to_scrape=None):
    
    s = Scraper()
    db = DatabaseInteraction()
    counter = 0

    if get_genre:

        desired_section = 'Most influential artists'
        sel = "div#content div.divided-layout div.layout-container.leftContent div"

        # scrape and write artists to DB
        artists = s.get_artist_urls(url, sel, desired_section)
        db.write_artists(artists)

    if artists_to_scrape is None:
        n_artists_to_scrape = 100
    else:
        n_artists_to_scrape = len(artists_to_scrape)

    for i in range(n_artists_to_scrape):
        # get next artist to scrape
        if artists_to_scrape is None:
            artist = db.get_next_artist_to_scrape()

        else:
            artist = db.get_artist_info(artists_to_scrape[i])

        # scrape artists for songs and write songs to DB
        if get_first_artist_songs or counter != 1:
            songs = s.get_artist_songs(artist)
            db.write_songs(songs)
            print(f'Getting songs for {artist["name"]}')
        
        # get next song to scrape
        n_songs_to_scrape = db.count_songs_to_scrape(artist['id'])
        for _ in range(n_songs_to_scrape):
            song = db.get_next_song_to_scrape(artist['id'])
            sampled_in, contains, new_artists = s.get_song_connections(song['url'])
            db.write_artists(new_artists)
            db.write_songs(sampled_in)
            db.write_songs(contains)
            db.update_scraped_status('songs', song['id'], 1)

            for song_dict in sampled_in:
                sample_id = db.get_song_id(song_dict['url'])
                db.insert_contains_sample(song['id'], sample_id)
        
        db.update_scraped_status('artists', artist['id'], 1)
        counter += 1

artists_to_scrape = [10, 29, 4601, 485, 489, 1749, 60, 476, 350, 3351]
main(get_genre=False, get_first_artist_songs=True, artists_to_scrape=artists_to_scrape)











