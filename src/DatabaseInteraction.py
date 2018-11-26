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
                INSERT INTO artists (name, url)
                
                SELECT '{artist["name"]}',
                        '{artist["url"]}'
                WHERE NOT EXISTS (
                            SELECT name, url FROM artists 
                            WHERE name = '{artist["name"]}' 
                            AND url = '{artist["url"]}'
                            );
                        """

            self.cur.execute(query)
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
                INSERT INTO songs (name, url)
                
                SELECT '{song["name"]}',
                        '{song["url"]}'
                WHERE NOT EXISTS (
                            SELECT name, url FROM artists 
                            WHERE name = '{song["name"]}' 
                            AND url = '{song["url"]}'
                            );
                        """

            self.cur.execute(query)
            self.conn.commit()
