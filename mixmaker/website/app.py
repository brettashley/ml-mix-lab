import pickle
import pandas as pd
from flask import Flask, request, render_template, jsonify
from ..web_functions import WebFunctionHandler


# with open('.pkl') as f:
#     model = pickle.load(f)

app = Flask(__name__, static_url_path="")

wfh = WebFunctionHandler()

@app.route('/')
def index():
    """Return the main page."""
    # all_songs = db.get_song_and_artist_names()
    n_artists = 10
    artist_names = wfh.get_unique_artist_names()[:10].to_html()
    n_artists, artists_selection = wfh.get_artist_searchable(n_artists)
    return render_template('index.html',
                                artist_names=artist_names,
                                artists_selection=artists_selection,
                                n_artists=n_artists)


@app.route('/get_selector_for_songs/<int:artist_id>')
def get_selector_for_songs(artist_id):
    artist_songs = wfh.get_selector_for_songs(artist_id)
    return artist_songs

@app.route('/get_predictions/<int:song_id>')
def get_predictions(song_id):
    data = wfh.get_predictions(song_id)
    return render_template('recommender_table.html', data=data)


# @app.route('/artist/<int:artist_id>')
# def artist_songs(artist_id):
#     """Return songs for an artist."""
#     artist_songs = wfh.get_selector_for_songs(artist_id)
#     results = wfh.get_predictions(song_id)
#     return render_template('index.html',
#                                 artist_songs=artist_songs,
#                                 results=results)