import selenium
from selenium.webdriver import Firefox, Chrome
import time
from DatabaseInteraction import DatabaseInteraction

class Scraper():
    """A web scraper specific to https://www.whosampled.com"""

    def __init__(self, url, browser=Firefox()):
        self.b = browser
        self.start_url = url
        self.b.get(self.start_url)


    def _accept_cookies(self):
        """Finds 'Accept Cookies' Button if it exists and clicks"""
        try:
            button = self.b.find_element_by_css_selector('button.qc-cmp-button')
            button.click()
        except selenium.common.exceptions.NoSuchElementException:
            pass


        # desired_section = 'Most influential artists'
        # sel = "div#content div.divided-layout div.layout-container.leftContent div"

    def find_desired_section(self, sel, desired_section):
        """Finds a section on a webpage

        Parameters
        ----------
        sel : string, css_selector
        desired_section : string, title of desired section

        Returns
        -------
        object : webpage section 
        """
        self._accept_cookies()
        sect_divs = self.b.find_elements_by_css_selector(sel)
        for i, div in enumerate(sect_divs):
            if div.text.startswith(desired_section):
                return sect_divs[i+1]

    def get_artist_urls(self, artists_section):
        """Finds artist URL's on a genre page

        Parameters
        ----------
        artists_section : object, css_selector
        desired_section : string, title of desired section

        Returns
        -------
        generator : list of dictionaries for each artist name and url
        """
        artist_tiles = artists_section.find_elements_by_css_selector('li')
        artists = {}
        for tile in artist_tiles:
            tile.location_once_scrolled_into_view
            time.sleep(2)
            a = tile.find_element_by_css_selector('a')
            artist_name = tile.text
            artists = {'name': artist_name,
                    'url': a.get_attribute('href')}
            


    def get_artist_songs(self, artist_url_dict):
        self._accept_cookies()
        sel = "div#content div.artistContent"
        section_divs = self.b.find_element_by_css_selector(sel)
        tracks = section_divs.find_elements_by_css_selector('h3.trackName')
        track_urls = {}
        for track in tracks:
            a = track.find_element_by_css_selector('a')
            yield {'track_name': track.text,
                   'url': a.get_attribute('href')}

    def get_song_connections(self, song_url):
        """Navigates to song page and scrapes all song connections and artist links"""
        try:
            sel = "div#content\
             div.divided-layout\
             div.list-content-action-mobile"
            button = self.b.find_element_by_css_selector(sel)
            a = button.find_element_by_css_selector('a')
            url = a.get_attribute('href')
            self._get_was_sampled_in(url)
        except selenium.common.exceptions.NoSuchElementException:
            self._get_was_sampled_in(song_url)
        



    def _get_contains_samples(self, song_url):
        pass

    def _get_was_sampled_in(self, song_url):
        pass



    def get(self, url):
        self.b.get(url)
