import pickle
from flask import Flask, request, render_template, jsonify


# with open('.pkl') as f:
#     model = pickle.load(f)

app = Flask(__name__, static_url_path="")

@app.route('/')
def index():
    """Return the main page."""
    ajj='stupendous'
    return render_template('index.html', ajj=ajj)