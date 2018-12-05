import psycopg2
import pandas as pd
from psycopg2.extras import Json
from psycopg2 import sql


class DatabaseInteraction():

    def __init__(self, db_name='mixmaker', host='localhost'):
        self.db_name = db_name
        self.conn = psycopg2.connect(dbname=self.db_name, host=host)
        self.cur = self.conn.cursor()

    def get_table(self, table_name, filters_as_where_clause=''):
        query = " SELECT * FROM {}" + filters_as_where_clause + ";"

                
        self.cur.execute(sql.SQL(query)
                    .format(sql.Identifier(table_name)))
        self.conn.commit()
        table = list(self.cur)

        query = """ 
                SELECT column_name 
                FROM information_schema.columns
                WHERE table_name = %s
                ;""" 

                
        self.cur.execute(sql.SQL(query), (table_name,))
        self.conn.commit()
        col_names = [x for (x,) in self.cur]

        return pd.DataFrame(table, columns=col_names)


    def write_artists(self, artist_urls, return_artist_id=False):
        '''
        Parameters
        ----------
        artists : list of dictionaries

        Returns
        -------
        self :  Writes artist to database
        '''
        for artist in artist_urls:
            if return_artist_id:
                query = """   
                INSERT INTO artists (name, url, scraped)
                SELECT %s, %s, 0
                WHERE %s NOT IN (
                            SELECT url FROM artists
                            )
                RETURNING id;
                
                        """
            else:
                query = """   
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
                song['artist_id'] = [x for (x,) in self.cur][0]

            query = f"""   
                INSERT INTO songs (artist_id, name, url, scraped)
                SELECT %s, %s, %s, 0
                WHERE %s NOT IN (
                            SELECT url FROM songs
                            );
                        """
            self.cur.execute(query, (
                 song["artist_id"],
                 song["name"],
                 song["url"],
                 song["url"]))
            self.conn.commit()


    def update_scraped_status(self, table, id_to_update, status):
        
        query = """
                UPDATE {}
                SET scraped = %s
                WHERE id = %s
                ;"""

        self.cur.execute(
            sql.SQL(query)
                .format(sql.Identifier(table))
            , (status, id_to_update))
        self.conn.commit()




    def get_next_artist_to_scrape(self):
        """ 
        Returns
        -------
        arist :  dictionary of next artist to scrape      
        """
        query = """
                SELECT id, url, name FROM artists
                WHERE scraped = 0
                ORDER BY id
                LIMIT 1
                """

        self.cur.execute(query)
        self.conn.commit()
        output = list(self.cur)
        return {'id' : output[0][0],
                'url' : output[0][1],
                'name': output[0][2]}

    def get_next_song_to_scrape(self, artist_id=None):
        """ 
        Returns
        -------
        arist :  dictionary of next artist to scrape      
        """
        if artist_id is None:
            query = """
                    SELECT id, url FROM songs
                    WHERE scraped = 0
                    ORDER BY id
                    LIMIT 1
                    """
            self.cur.execute(query)
        
        else:
            query = """
                    SELECT id, url FROM songs
                    WHERE scraped = 0
                    AND artist_id = %s
                    ORDER BY id
                    LIMIT 1
                    """
            self.cur.execute(query, (artist_id,))

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

        self.cur.execute(query, (artist_id,))
        self.conn.commit()
        return [x for (x,) in self.cur][0]

    
    def insert_contains_sample(self, song_id, sample_song_id):
        '''
        Parameters
        ----------
        song_urls : list of dictionaries

        Returns
        -------
        self :  Writes songs to database
        '''
        query = f"""   
            INSERT INTO connections (song_id, sampled_by_song_id, is_connected)
            
            SELECT %s, %s, 1
                    
            WHERE (%s, %s) NOT IN (
                        SELECT song_id, sampled_by_song_id FROM connections
                        );
                    """
        self.cur.execute(query, (
                song_id,
                sample_song_id,
                song_id,
                sample_song_id))
        self.conn.commit()

    def get_song_id(self, song_url):
        query = """   
                SELECT id
                FROM songs    
                WHERE url = %s;
                """
        self.cur.execute(query, (song_url,))
        self.conn.commit()
        return [x for (x,) in self.cur][0]

    def get_artist_info(self, artist_id=None, url=None):
        """ 
        Returns
        -------
        arist :  dictionary of desired artist   
        """
        if artist_id is not None:
            query = """
                    SELECT id, url, name, scraped FROM artists
                    WHERE id = %s
                    """
            self.cur.execute(query, (artist_id,))
        elif url is not None:
            query = """
                    SELECT id, url, name, scraped FROM artists
                    WHERE url = %s
                    """
            self.cur.execute(query, (url,))

        self.conn.commit()
        output = list(self.cur)
        return {'id' : output[0][0],
                'url' : output[0][1],
                'name': output[0][2],
                'scraped': output[0][3]}
        
    def get_next_artist_for_spotify(self):
        query = """   
                SELECT a.name, count(s.artist_id) as artist_freq
                FROM artists a
                JOIN songs s
                ON a.id = s.artist_id
                GROUP BY a.id
                HAVING a.scraped_spotify = 0
                ORDER BY artist_freq DESC
                LIMIT 1;
                """
        self.cur.execute(query)
        self.conn.commit()


    def update_scraped_spotify_status(self, table, id_to_update, status):
        query = """
                UPDATE {}
                SET scraped_spotify = %s
                WHERE id = %s
                ;"""

        self.cur.execute(
            sql.SQL(query)
                .format(sql.Identifier(table))
            , (status, id_to_update))
        self.conn.commit()


    def get_song_id_with_title(self, song_title, artist_id):
        query = """
                SELECT id, name, url
                FROM songs
                WHERE name = %s
                AND artist_id = %s
                """

        self.cur.execute(query, (song_title, artist_id))
        self.conn.commit()
        result = list(self.cur)
        if len(result)==0:
            None
        else:
            return [x for x in result][0]

    def get_predictions_for_song(self, song_id):
        # query = """
        #         SELECT id, name, url
        #         FROM songs
        #         WHERE name = %s
        #         AND artist_id = %s
        #         """

        # self.cur.execute(query, (song_title, artist_id))
        # self.conn.commit()
        # result = list(self.cur) 
        pass

    
    def get_song_and_artist_names(self, artist_id = None, song_id=None):
            
        if (artist_id, song_id) == (None, None):
            query = """
                SELECT a.name, s.name, s.url
                FROM songs s
                LEFT JOIN artists a
                ON s.artist_id = a.id
                ;"""

            self.cur.execute(sql.SQL(query))

        elif song_id is not None:
            query = """
                SELECT a.name, s.name, s.url
                FROM songs s
                LEFT JOIN artists a
                ON s.artist_id = a.id
                WHERE s.id = %s
                ;"""

            self.cur.execute(sql.SQL(query), (song_id,))

        elif artist_id is not None:
            query = """
                SELECT a.name, s.name, s.url
                FROM songs s
                LEFT JOIN artists a
                ON s.artist_id = a.id
                WHERE a.id = %s
                ;"""

            self.cur.execute(sql.SQL(query), (artist_id,))

        self.conn.commit()
        df = pd.DataFrame(list(self.cur),
                          columns=['artist_name', 'song_name', 'song_url'])
        
        df['correct_artist_url'] = (df['song_url']
                                    .apply(self._extract_real_artist_url))

        artists = self.get_table('artists')
        merged = df.merge(artists, left_on='correct_artist_url', right_on='url')
        merged['correct_artist_name'] = merged.apply(self._correct_artist_names, axis=1)

        output =  merged.loc[:,['correct_artist_name', 'song_name']]
        output.columns = ['artist_name', 'song_name']
        return output

        
    def _extract_real_artist_url(self, url):
        splits = url.split('/')
        if (splits[5] == 'tv') or (splits[5] == 'movie'):
            return '/'.join(splits[:5]) + '/' 
        else:
            return '/'.join(splits[:4]) + '/'
    
    def _correct_artist_names(self, df):
        if df['artist_name'] != df['name']:
            return df['name']
        else:
            return df['artist_name']




    def strip_years_from_name(self, update_all=True, artist_id=None, song_id=None):

        query = """
            UPDATE songs
            SET name = REGEXP_REPLACE(name, ' \((19|20)\d{2}\)', '')
            ;"""

        self.cur.execute(sql.SQL(query))
        self.conn.commit()



    def fix_similar_url_ids(self):
        is_output = True
        while is_output:
            query = """   
                    SELECT id, url from songs
                    WHERE (url LIKE '%\%28%'
                    OR url LIKE '%\%29%')
                    AND checked = 0
                    ORDER BY id
                    LIMIT 1;
                    """
            self.cur.execute(query)
            self.conn.commit()
            results = [x for x in self.cur]
            if len(results) != 0:
                current_id = results[0][0]
                current_url = results[0][1]

                correct_song_url = current_url.replace('%28', '(').replace('%29', ')')
                query = """   
                        SELECT id, url from songs
                        WHERE url = %s
                        LIMIT 1;
                        """
                self.cur.execute(query, (correct_song_url,))
                self.conn.commit()
                results = [x for x in self.cur]
                if len(results) == 1:
                    correct_id = results[0][0]

                    update_song_id = """   
                                    UPDATE connections
                                    SET song_id = %s
                                    WHERE song_id = %s;
                                    """
                    update_sampled = """   
                                    UPDATE connections
                                    SET sampled_by_song_id = %s
                                    WHERE sampled_by_song_id = %s;
                                    """
                    update_checked = """   
                                    UPDATE songs
                                    SET checked = 1
                                    WHERE id = %s;
                                    """
                    self.cur.execute(update_song_id, (correct_id, current_id))
                    self.cur.execute(update_sampled, (correct_id, current_id))
                    self.cur.execute(update_checked, (current_id, ))                                        
                    self.conn.commit()
                    print(f'updated {(current_id, current_url)} to \n {correct_id, correct_song_url} \n')
                else:
                    # print(f'{current_id} Does not need update')
                    update_checked = """   
                                    UPDATE songs
                                    SET checked = 1
                                    WHERE id = %s;
                                    """
                    self.cur.execute(update_checked, (current_id, ))
                                                                    
                    self.conn.commit()
            else:
                is_output = False
                print('done')


