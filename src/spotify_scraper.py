
import spotipy
import spotipy.util as util


class SpotifyScraper():

    def __init__(self, token):
        self.spotify = spotipy.Spotify(auth=token)

    def get_artist_uri(self, artist_name):
        artist_uri = []
        followers = []
        results = self.spotify.search(artist_name, type='artist')
        for item in results['artists']['items']:
            if item['name'] == artist_name:
                artist_uri.append(item['uri'])
        if len(artist_uri) == 0:
            return 'No Match'
        if len(artist_uri) == 1:
            return artist_uri[0]
        elif len(artist_uri) > 1:
            return artist_uri

    def get_artist_albums(self, artist_uri):
        results = self.spotify.artist_albums(artist_id=artist_uri)
        albums = results['items']
        while results['next']:
            results = ss.spotify.next(results)
            albums.extend(results['items'])
        return [album['uri'] for album in albums]
      
    
    def get_album_tracks(self, album_uri):
        results = self.spotify.album_tracks(album_uri)
        tracks = results['items']
        while results['next']:
            results = self.spotify.next(results)
            tracks.extend(results['items'])
        return [track['uri'] for track in tracks]


    

    




