import psycopg2
import pandas as pd
from psycopg2.extras import Json
from psycopg2 import sql
import re


class DatabaseInteraction():

    def __init__(self, db_name='mixmaker', host='localhost'):
        self.db_name = db_name
        self.conn = psycopg2.connect(dbname=self.db_name, host=host)
        self.cur = self.conn.cursor()
        self.artists = None

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
                INSERT INTO songs (artist_id, name, url, scraped, scraped_spotify,
                    corrected_name, corrected_artist_id, checked)
                SELECT %s, %s, %s, 0, 0, '', 0, 0
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




    def get_next_artist_to_scrape(self, sort_by_freq=True):
        """ 
        Returns
        -------
        arist :  dictionary of next artist to scrape      
        """
        if sort_by_freq:
            query = """
                    SELECT a.id, a.url, a.name 
                    FROM artists a
                    LEFT JOIN songs s
                    ON a.id = s.artist_id
                    WHERE a.scraped = 0
                    GROUP BY a.id, a.url, a.name
                    ORDER BY count(s.artist_id) DESC
                    LIMIT 1
                    """
        else:
            query = """
                    SELECT id, url, name 
                    FROM artists
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

        self.cur.execute(query, (
                sample_song_id,
                song_id,
                sample_song_id,
                song_id))
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
        """ 
        Returns
        -------
        arist :  dictionary of next artist to scrape      
        """
        query = """
                SELECT a.id, a.name 
                FROM artists a
                LEFT JOIN songs s
                ON a.id = s.artist_id
                WHERE a.scraped_spotify = 0
                GROUP BY a.id, a.name
                ORDER BY count(s.artist_id) DESC
                LIMIT 1
                """

        self.cur.execute(query)
        self.conn.commit()
        output = list(self.cur)
        return {'id' : output[0][0],
                'name': output[0][1]}


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
        query = """
                SELECT a.name, s.corrected_name, s.url
                FROM predictions p
                LEFT JOIN songs s
                ON p.item_song_id = s.id
                LEFT JOIN artists a
                ON s.corrected_artist_id = a.id
                WHERE p.user_song_id = %s
                """

        self.cur.execute(query, (song_id,))
        self.conn.commit()
        return pd.DataFrame(list(self.cur), columns=['artist', 'song', 'url'])
        

    def get_artist_names(self):
        query = """   
                SELECT id, name
                from artists;
                """
        self.cur.execute(query)
        self.conn.commit()
        return pd.DataFrame([x for x in self.cur], columns=['id', 'name'])

    
    def get_song_and_artist_names(self, artist_id = None, song_id=None):
            
        if (artist_id, song_id) == (None, None):
            query = """
                SELECT s.id, a.name, s.corrected_name
                FROM songs s
                LEFT JOIN artists a
                ON s.corrected_artist_id = a.id
                ;"""

            self.cur.execute(sql.SQL(query))

        elif song_id is not None:
            query = """
                SELECT s.id, a.name, s.corrected_name
                FROM songs s
                LEFT JOIN artists a
                ON s.corrected_artist_id = a.id
                WHERE s.id = %s
                ;"""

            self.cur.execute(sql.SQL(query), (song_id,))

        elif artist_id is not None:
            query = """
                SELECT s.id, a.name, s.corrected_name
                FROM songs s
                LEFT JOIN artists a
                ON s.corrected_artist_id = a.id
                WHERE s.corrected_artist_id = %s
                ;"""

            self.cur.execute(sql.SQL(query), (artist_id,))

        self.conn.commit()
        return pd.DataFrame(list(self.cur),
                          columns=['id', 'artist_name', 'song_name'])
        



    def _write_corrected_artist_ids(self):
        is_output = True
        while is_output:
            if self.artists is None:
                self.artists = self.get_table('artists')

            query = """
                    SELECT id, artist_id, url
                    FROM songs
                    WHERE corrected_artist_id = 0
                    ORDER BY id
                    LIMIT 1;
                    """
            self.cur.execute(query)
            self.conn.commit()
            df = pd.DataFrame([x for x in self.cur], columns=['id', 'artist_id', 'song_url'])
            if len(df) > 0:

                df['correct_artist_url'] = (df['song_url']
                                    .apply(self._extract_real_artist_url))

                merged = df.merge(self.artists, left_on='correct_artist_url', right_on='url',
                                                             suffixes=('_song', '_artist'))
                
                if len(merged) > 0:    
                    merged['corrected_artist_id'] = merged.apply(self._correct_artist_ids, axis=1)                
                    corrected_id = merged.loc[0, 'corrected_artist_id'].astype(float)
                else:
                    corrected_id = df.loc[0, 'artist_id'].astype(float)

                id_song = df.loc[0, 'id'].astype(float)


                query = """
                        UPDATE songs
                        SET corrected_artist_id = %s
                        WHERE id = %s
                        """

                self.cur.execute(query, (corrected_id, id_song))
                self.conn.commit()
            else:
                is_output = False
                print('done')
        
    def _extract_real_artist_url(self, url):
        splits = url.split('/')
        if (splits[3] == 'tv') or (splits[3] == 'movie'):
            return '/'.join(splits[:5]) + '/' 
        else:
            return '/'.join(splits[:4]) + '/'
    
    def _correct_artist_names(self, df):
        if df['artist_name'] != df['name']:
            return df['name']
        else:
            return df['artist_name']
    
    def _correct_artist_ids(self, df):
        if df['artist_id'] != df['id_artist']:
            return df['id_artist']
        else:
            return df['artist_id']


    def _fix_song_titles(self):
        songs = self.get_table('songs')
        songs['correct_song_titles'] = songs.apply(self._find_replace_for_song_titles)



    def _find_replace_for_song_titles(self):
        is_output = True
        while is_output:
            query = """
                    SELECT id, name
                    FROM songs
                    WHERE corrected_name = ''
                    LIMIT 1;
                    """
            self.cur.execute(query)
            self.conn.commit()
        
            song = [x for x in self.cur]

            if len(song) > 0:
                song_id = song[0][0]
                split = song[0][1].split('\n')
                new_title = re.sub(r' \((19|20)[0-9]{2}\)', '' ,split[0])

                query = """
                        UPDATE songs
                        SET corrected_name = %s
                        WHERE id = %s
                        """
                self.cur.execute(query, (new_title, song_id))
                self.conn.commit()
            else:
                is_output = False
                print('done')


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

        
    def write_symmetric_connections(self):
        is_output=True
        counter = 0
        while is_output:
            query = """
                    SELECT song_id, sampled_by_song_id
                    FROM connections
                    WHERE checked = 0
                    LIMIT 1
                    """
            self.cur.execute(query)
            self.conn.commit()
            ids = [x for x in self.cur]
            if len(ids) > 0:
                song_id = ids[0][0]
                sample_song_id = ids[0][1]


                query = f"""   
                    INSERT INTO connections (song_id, sampled_by_song_id, is_connected)
                    
                    SELECT %s, %s, 1
                            
                    WHERE (%s, %s) NOT IN (
                                SELECT song_id, sampled_by_song_id FROM connections
                                );
                            """

                self.cur.execute(query, (
                        sample_song_id,
                        song_id,
                        sample_song_id,
                        song_id))
                self.conn.commit()

                query = """
                        UPDATE connections
                        SET checked = 1
                        WHERE song_id = %s
                        AND sampled_by_song_id = %s
                        ;"""

                self.cur.execute(
                    sql.SQL(query),
                    (song_id, sample_song_id))
                self.conn.commit()


                counter += 1
                if counter % 100 == 0:
                    print(counter)
            else:
                is_output=False

    def write_song_to_song_connection(self):
        query = """
                SELECT song_id
                FROM connections
                """
        self.cur.execute(query)
        self.conn.commit()
        ids = [x for (x,) in self.cur]
        ids_set = set(ids)
        for song_id in ids_set:
            query = """   
                    INSERT INTO connections (song_id, sampled_by_song_id, is_connected)
                    SELECT %s, %s, 1
                    WHERE (%s, %s) NOT IN (
                            SELECT song_id, sampled_by_song_id FROM connections
                            )
                    """

            self.cur.execute(query, (
                    song_id,
                    song_id,
                    song_id,
                    song_id))
            self.conn.commit()