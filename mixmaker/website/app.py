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
    search = 'search'
    all_songs = db.get_song_and_artist_names()
    artist_names = pd.DataFrame(all_songs['artist_name'].unique(),
                     columns=['artist_name'])
    
    artist_songs = pd.DataFrame(filtered_songs, columns=['song_name'])
    return render_template('index.html',
                                search=search,
                                all_songs=all_songs,
                                artist_names=artist_names,
                                artist_songs=artist_songs)

@app.route('/<artist>')
def artist_songs(artist):
    return  db.get_artist_songs(artist) # write to take in artist name
    

@app.route('/recommendations/<id>')   
def recommendations(id):
    return db.get_recommendations_for_song(song_id)