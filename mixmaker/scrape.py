#!/usr/bin/env python3

import selenium
from selenium.webdriver import Firefox, Chrome
import time
from scraper import Scraper
from DatabaseInteraction import DatabaseInteraction
import numpy as np


def main(url=None,
         get_genre=True,
         get_first_artist_songs=True,
         artists_to_scrape=None,
         db_name='mixmaker2',
         section='Most influential'):
    
    s = Scraper()
    db = DatabaseInteraction(db_name=db_name)
    counter = 0

    if get_genre:

        sel = "div#content div.divided-layout div.layout-container.leftContent div"

        # scrape and write artists to DB
        artists = s.get_artist_urls(url, sel, section)
        db.write_artists(artists)

        artists_to_scrape = []
        scraped_status = []
        for artist in artists:
            artist_dict = db.get_artist_info(url=artist["url"])
            if artist_dict["scraped"] == 0:
                artists_to_scrape.append(artist_dict["id"])

    print(f'Scraping artists: {artists_to_scrape}')
    if artists_to_scrape is None:
        n_artists_to_scrape = 5
    else:
        n_artists_to_scrape = len(artists_to_scrape)

    for i in range(n_artists_to_scrape):
        # get next artist to scrape
        if artists_to_scrape is None:
            artist = db.get_next_artist_to_scrape()

        else:
            artist = db.get_artist_info(artist_id=artists_to_scrape[i])

        # scrape artists for songs and write songs to DB
        if get_first_artist_songs or counter != 0:
            print(f'Getting songs for {artist["name"]}')
            songs = s.get_artist_songs(artist)
            db.write_songs(songs)
            
        
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

            for song_dict in contains:
                sampled_id = db.get_song_id(song_dict['url'])
                db.insert_contains_sample(sampled_id, song['id'])

        db.update_scraped_status('artists', artist['id'], 1)
        counter += 1

def scrape_songs():
    db = DatabaseInteraction()
    s = Scraper()
    while db.get_next_song_to_scrape():
        song = db.get_next_song_to_scrape()
        # print(song['url'])
        sampled_in, contains, new_artists = s.get_song_connections(song['url'])
        db.write_artists(new_artists)
        db.write_songs(sampled_in)
        db.write_songs(contains)
        db.update_scraped_status('songs', song['id'], 1)

        for song_dict in sampled_in:
            sample_id = db.get_song_id(song_dict['url'])
            db.insert_contains_sample(song['id'], sample_id)

        for song_dict in contains:
            sampled_id = db.get_song_id(song_dict['url'])
            db.insert_contains_sample(sampled_id, song['id'])







# artists_to_scrape = [485, 489, 1749, 60, 476, 350, 3351]

# main(url=url_soul_funk_disco, get_genre=False, get_first_artist_songs=True)

# main(url='https://www.whosampled.com/genre/Soul-Funk-Disco/',
#      get_genre=False,
#      get_first_artist_songs=False,
#      db_name='mixmaker')

# artists_to_scrape = [7993, 7940, 8896, 317, 641, 572, 2954, 4465, 10014, 7638]

# main(url='https://www.whosampled.com/genre/Hip-Hop/',
#      get_genre=False,
#      get_first_artist_songs=False,
#      db_name='mixmaker',
#      section='Most popular',
#      artists_to_scrape = artists_to_scrape)

main(url='https://www.whosampled.com/genre/Hip-Hop/',
     get_genre=True,
     get_first_artist_songs=True,
     db_name='mixmaker',
     section='Most influential')

main(url='https://www.whosampled.com/genre/Electronic-Dance/',
     get_genre=True,
     db_name='mixmaker',
     section='Most influential')

main(url='https://www.whosampled.com/genre/Electronic-Dance/',
     get_genre=True,
     db_name='mixmaker',
     section='Most popular')


# scrape_songs()










