import pickle
import pandas as pd
from flask import Flask, request, render_template, jsonify
from ..database_interaction import DatabaseInteraction


# with open('.pkl') as f:
#     model = pickle.load(f)

app = Flask(__name__, static_url_path="")


db = DatabaseInteraction()

@app.route('/')
def index():
    """Return the main page."""
    all_songs = db.get_song_and_artist_names()
    all_songs_dict = all_songs.to_dict()
    artist_names = pd.DataFrame(all_songs['artist_name'].unique(),
                     columns=['artist_name'])
    artist_names_data = artist_names[:10].to_html()
    
    artist_songs = ''
    return render_template('index.html',
                                artist_names=artist_names_data,
                                artist_songs=artist_songs)

# @app.route('/<artist>')
# def artist_songs(artist):
#     """Return songs for an artist."""
#     artist_songs =  db.get_artist_songs(artist) # write to take in artist name
#     return render_template('index.html',
#                                 artist_songs=artist_songs)
    

# @app.route('/recommendations/<id>')   
# def recommendations(id):
#     recs = db.get_recommendations(id)
#     return render_template('index.html',
#                                 recs=recs)