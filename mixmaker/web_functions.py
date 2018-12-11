
import pandas as pd
import numpy as np
from .database_interaction import DatabaseInteraction

db = DatabaseInteraction()
class WebFunctionHandler():

    def __init__(self):
        self.db = DatabaseInteraction()

    def filter_songs_by_artist(self, df, id):
        return df.loc[:,'corrected_artist_id']

    def get_unique_artist_names(self):
        return self.db.get_artist_names()

    def get_songs_for_artist(self, artist_id):
        return (self.db.get_song_and_artist_names(artist_id=artist_id)
                    .to_html())
    
    def get_artist_selections(self, n_artists):
        artists = self.db.get_artist_names()
        artists = artists.sort_values('id').set_index('id')
        output = '<select id="artists_selection" size="5">'
        counter = 0
        for i, artist in artists.iterrows():
            if counter < n_artists:
                artist_id = i
                artist_name = artist[0]
                output += f'\n    <option value="{artist_id}">{artist_name}</option>'
                counter += 1
            else:
                break
        return output + '\n</select>'

    def get_selector_for_songs(self, artist_id):
        songs_df = self.db.get_artist_songs_with_predictions(artist_id=artist_id)
        songs_df = songs_df.sort_values('song_name').set_index('id')
        output = '<select id="artist_songs" size="5">'
        for i, song in songs_df.iterrows():
                song_id = i
                song_name = song[1]
                output += f'\n    <option value="{song_id}">{song_name}</option>'
        return output + '\n</select>'

    def get_predictions(self, song_id):
        results_df = db.get_predictions_for_song(song_id)
        return results_df.loc[:,['artist', 'song', 'url']].to_dict(orient='records')


    
        

    







