import psycopg2
import pandas as pd
from psycopg2.extras import Json


class DatabaseInteraction():

    def __init__(self, db_name='mixmaker'):
        self.db_name = db_name
        self.conn = psycopg2.connect(dbname=self.db_name, host='localhost')
        self.cur = self.conn.cursor()

    def write_artists(self, artist_urls):
        '''
        Parameters
        ----------
        artists : list of dictionaries

        Returns
        -------
        self :  Writes artist to database
        '''
        for artist in artist_urls:
            query = f"""   
                INSERT INTO artists (name, url, scraped)
                
                SELECT %s, %s, 0
                        
                WHERE %s NOT IN (
                            SELECT url FROM artists
                            );
                        """
            self.cur.execute(query, (
                 artist["name"],
                 artist["url"],
                 artist["url"]))
            self.conn.commit()

    def write_songs(self, song_urls):
        '''
        Parameters
        ----------
        song_urls : list of dictionaries

        Returns
        -------
        self :  Writes songs to database
        '''
        for song in song_urls:
            query = f"""   
                INSERT INTO songs (artist_id, name, url, scraped)
                
                SELECT %s, %s, %s, 0
                        
                WHERE %s NOT IN (
                            SELECT url FROM artists
                            );
                        """
            self.cur.execute(query, (
                 song["artist_id"],
                 song["track_name"],
                 song["url"],
                 song["url"]))
            self.conn.commit()


    def update_scraped_status(self, table, id_to_update, status):
        
        query = f"""
                UPDATE %s
                SET scraped = %s
                WHERE id = %s
                ;"""

        self.cur.execute(query, (table, status, id_to_update))
        self.conn.commit()




    def get_next_artist_to_scrape(self):
        """ 
        Returns
        -------
        arist :  dictionary of next artist to scrape      
        """
        query = """
                SELECT id, url FROM artists
                WHERE scraped = 0
                ORDER BY id
                LIMIT 1
                """

        self.cur.execute(query)
        self.conn.commit()
        output = list(self.cur)
        return {'id' : output[0][0],
                'url' : output[0][1]}

    def get_next_song_to_scrape(self):
        """ 
        Returns
        -------
        arist :  dictionary of next artist to scrape      
        """
        query = """
                SELECT id, url FROM songs
                WHERE scraped = 0
                ORDER BY id
                LIMIT 1
                """

        self.cur.execute(query)
        self.conn.commit()
        output = list(self.cur)
        return {'id' : output[0][0],
                'url' : output[0][1]}

    def count_songs_to_scrape(self, artist_id):
        query = """
                SELECT count(*) FROM songs
                WHERE scraped = 0
                """

        self.cur.execute(query)
        self.conn.commit()
        return list(self.cur)[0][0]



