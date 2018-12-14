
import spotipy
import spotipy.util as util
import json
import numpy as np

class SpotifyScraper():

    def __init__(self, token=None, my_username='brett.mccoubrey@gmail.com'):
        
        self.token = token

        if self.token is None:
            with open('/Users/brettashley/.secrets/spotify.json') as f:
                params = json.load(f)

            self.token = util.prompt_for_user_token(
                            username=my_username,
                            scope='user-library-read',
                            client_id=params['client_id'],
                            client_secret=params['secret_key'],
                            redirect_uri=params['redirect']
                            )
        self.spotify = spotipy.Spotify(auth=self.token, trace=False)


    def get_artist_uri(self, artist_name):
        """Search artist by name and return uri exact match or most popular match
        
        Parameters
        ----------
        artist_name: string, name of artist

        Returns
        -------
        uri : string
        
        """
        artist_uri = []
        results = self.spotify.search(artist_name, type='artist')
        for item in results['artists']['items']:
            if item['name'] == artist_name:
                artist_uri.append(item['uri'])
        if len(artist_uri) == 0:
            return 'No Match'
        if len(artist_uri) == 1:
            return artist_uri[0]
        elif len(artist_uri) > 1:
            return self._choose_most_popular_artist(results)

    def get_artist_albums(self, artist_uri):
        """Get all album uris for an artist
        Parameters
        ----------
        artist_uri: string

        Returns
        -------
        albums : list of strings
        """
        results = self.spotify.artist_albums(artist_id=artist_uri)
        albums = results['items']
        while results['next']:
            results = self.spotify.next(results)
            albums.extend(results['items'])
        return [album['uri'] for album in albums]
      
    
    def get_album_tracks(self, album_uri):
        """Get all track uris for an album
        Parameters
        ----------
        album_uri: list of strings

        Returns
        -------
        tracks : list of strings
        """
        results = self.spotify.album_tracks(album_uri)
        tracks = results['items']
        while results['next']:
            results = self.spotify.next(results)
            tracks.extend(results['items'])
        return [track['uri'] for track in tracks]

    
    def search_artist_get_tracks(self, artist_name):
        """Search an artist by name and return all track uris as a list
        Parameters
        ----------
        album_uri: list of strings

        Returns
        -------
        tracks : list of strings
        """

        artist_uri = self.get_artist_uri(artist_name)
        album_uris = self.get_artist_albums(artist_uri)

        tracks = []
        for album in album_uris:
            album_tracks = self.get_album_tracks(album)
            tracks.extend(album_tracks)
        return tracks

    def _choose_most_popular_artist(self, search_results):
        """From list of artist search results, return most pupular
        Parameters
        ----------
        search_results : output of spotify.search('artist_name')

        Returns
        -------
        artist_item : dictionary
        """
        results = search_results['artists']
        artists = np.chararray(results['total'], itemsize=50)
        popularity = np.zeros(results['total'])
        for n, artist in enumerate(results['items']):
            popularity[n] = artist['popularity']
            artists[n] = artist['uri']
        return artists[popularity.argmax()].decode('utf-8')
    
    def get_song_features(self, song_list, song_titles=None, song_features=None):
        """From list of artist search results, return most pupular
        Parameters
        ----------
        song_list : song uris as a list of strings

        Returns
        -------
        song_titles : song titles as list of strings
        song_features : list of dictionaries, one dictionary for each song
        """
        if song_titles is None:
            song_features = {}
            song_titles = {}
            
        
        if len(song_list) <= 50:
            features = self.spotify.audio_features(song_list)
            for i, song in enumerate(features):
                song_features.update({song_list[i]: song})

            results = self.spotify.tracks(song_list)
            for i, track in enumerate(results['tracks']):
                song_titles.update({song_list[i]: track['name']})
                # song_titles.append(track['name'])
            
            return song_titles, song_features

        else:
            features = self.spotify.audio_features(song_list[:50])
            for i, song in enumerate(features):
                song_features.update({song_list[i]: song})

            results = self.spotify.tracks(song_list[:50])
            for i, track in enumerate(results['tracks']):
                song_titles.update({song_list[i]: track['name']}) 
            # song_titles.extend(temp) 
            song_list = song_list[50:].copy()
            return self.get_song_features(song_list, song_titles, song_features)

            

        


    

    




