#!/usr/bin/env python3

import selenium
from selenium.webdriver import Firefox, Chrome
import time
from scraper import Scraper
from DatabaseInteraction import DatabaseInteraction

url_soul_funk_disco = 'https://www.whosampled.com/genre/Soul-Funk-Disco/'

def main(url):

    desired_section = 'Most influential artists'
    sel = "div#content div.divided-layout div.layout-container.leftContent div"

    s = Scraper()
    db = DatabaseInteraction()

    # scrape and write artists to DB
    artists = s.get_artist_urls(url, sel, desired_section)
    db.write_artists(artists)

    for _ in range(1):
        # get next artist to scrape
        artist = db.get_next_artist_to_scrape()

        # scrape artists for songs and write songs to DB
        songs = s.get_artist_songs(artist)
        db.write_songs(songs)
        current_artist_id = artist['id']
        

        # get next song to scrape
        n_songs_to_scrape = db.count_songs_to_scrape(artist['id'])
        for _ in range(n_songs_to_scrape):
            song = db.get_next_song_to_scrape()
            sampled_in, contains, new_artists = s.get_song_connections(song['url'])
            db.write_artists(new_artists)
            db.write_songs(sampled_in)
            db.write_songs(contains)
            db.update_scraped_status('songs', song['id'], 1)

            for song_dict in sampled_in:
                sample_id = db.get_song_id(song_dict['url'])
                db.insert_contains_sample(song['id'], sample_id)
        
        db.update_scraped_status('artists', current_artist_id, 1)

main(url_soul_funk_disco)











