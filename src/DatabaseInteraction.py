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

            if song['artist_id'] is None:

                query = f"""   
                    SELECT id FROM artists
                    WHERE url = %s
                            """
                self.cur.execute(query, (song['artist_url'],))
                self.conn.commit()
                song['artist_id'] = list(self.cur)[0][0]

            query = f"""   
                INSERT INTO songs (artist_id, name, url, scraped)
                
                SELECT %s, %s, %s, 0
                        
                WHERE %s NOT IN (
                            SELECT url FROM artists
                            );
                        """
            self.cur.execute(query, (
                 song["artist_id"],
                 song["name"],
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
                AND artist_id = %s
                """

        self.cur.execute(query, (artist_id))
        self.conn.commit()
        return list(self.cur)[0][0]

    
    def contains_sample(self, song_id, sample_song_ids):
        '''
        Parameters
        ----------
        song_urls : list of dictionaries

        Returns
        -------
        self :  Writes songs to database
        '''
        for song in sample_song_ids:
            query = f"""   
                INSERT INTO connections (song_id, sampled_by_song_id)
                
                SELECT %s, %s
                        
                WHERE %s, %s NOT IN (
                            SELECT song_id, sampled_by_song_id FROM connections
                            );
                        """
            self.cur.execute(query, (
                 song_id,
                 song,
                 song_id,
                 song))
            self.conn.commit()





