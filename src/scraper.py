import selenium
from selenium.webdriver import Firefox, Chrome
import time
import pandas as pd
from scipy import stats 

class Scraper():
    """A web scraper specific to https://www.whosampled.com"""

    def __init__(self, browser=None):
        if browser is None:
            self.b = Firefox()
        else:
            self.b = browser


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

    def get_artist_urls(self, url, genre_sel, artist_section):
        """Finds artist URL's on a genre page

        Parameters
        ----------
        artists_section : object, css_selector
        desired_section : string, title of desired section

        Returns
        -------
        artists : list of dictionaries for each artist name and url
        """
        self.get(url)

        artists_section = self.find_desired_section(genre_sel, artist_section)
        artist_tiles = artists_section.find_elements_by_css_selector('li')
        artists = []
        for tile in artist_tiles:
            tile.location_once_scrolled_into_view
            time.sleep(2)
            a = tile.find_element_by_css_selector('a')
            artist_name = tile.text
            artists.append({'name': artist_name,
                    'url': a.get_attribute('href')})
        return artists
            
            


    def get_artist_songs(self, artist_url_dict):
        """Finds artist URL's on a genre page

        Parameters
        ----------
        artists_section : object, css_selector
        desired_section : string, title of desired section

        Returns
        -------
        artists : list of dictionaries for each artist name and url
        """
        self.b.get(artist_url_dict['url'])
        self._accept_cookies()
        tracks_list = []

        last_page = False
        while last_page == False:
            self._get_one_page_songs(artist_url_dict, tracks_list)
            try:
                self._next_page()
            except selenium.common.exceptions.NoSuchElementException:
                last_page = True
        return tracks_list

    def _get_one_page_songs(self, artist_url_dict, tracks_list):

        sel = "div#content div.artistContent"
        section_divs = self.b.find_element_by_css_selector(sel)
        tracks = section_divs.find_elements_by_css_selector('h3.trackName')

        for track in tracks:
            a = track.find_element_by_css_selector('a')
            tracks_list.append({
                'artist_id': artist_url_dict['id'],
                'track_name': track.text,
                'url': a.get_attribute('href')
                })
        


    def get_song_connections(self, song_url):
        """Navigates to song page and scrapes all song connections and artist links"""

        # pd.DataFrame()
        self.get(song_url)

        sampled_in_song_list = []
        artist_list = []

        samples_song_list = []

        # was sampled in
        try:
            self._see_all('Was sampled in')
            last_page = False
            while last_page == False:
                self._get_samples(sampled_in_song_list, artist_list, 'Was sampled')
                try:
                    self._next_page()
                except selenium.common.exceptions.NoSuchElementException:
                    last_page = True

        except selenium.common.exceptions.NoSuchElementException:
                self._get_samples(sampled_in_song_list, artist_list, 'Was sampled')

        # samples
        try:
            self._see_all('Contains sample')
            last_page = False
            while last_page == False:
                self._get_samples(samples_song_list, artist_list, 'Contains sample')
                try:
                    self._next_page()
                except selenium.common.exceptions.NoSuchElementException:
                    last_page = True

        except selenium.common.exceptions.NoSuchElementException:
                self._get_samples(samples_song_list, artist_list, 'Contains sample')
        

        return sampled_in_song_list, samples_song_list, artist_list


    def _get_samples(self, sampled_in_song_list, artist_list, relation):

        sample_urls = []
        sel = "div#content\
               section"
        sections = self.b.find_elements_by_css_selector(sel)
        current_section = None
        for section in sections:
            try:
                header = section.find_element_by_css_selector('header')
                if header.text.startswith(relation):
                    current_section = section
            except selenium.common.exceptions.NoSuchElementException:
                continue
        sel = "div.listEntry.sampleEntry"
        song_sections = current_section.find_elements_by_css_selector(sel)
        for song in song_sections:
            a = song.find_element_by_css_selector('a')
            sample_urls.append(a.get_attribute('href'))

        for sample in sample_urls:
            artist_dict, song_dict = (
                self._get_metadata_from_sample_page(sample, relation))
            artist_list.append(artist_dict)
            sampled_in_song_list.append(song_dict)

            

    def _get_metadata_from_sample_page(self, sample_song_url, relation):

        time.sleep(round(stats.uniform(1,3).rvs(),2))
        self.get(sample_song_url)
        sel = "div#content\
               div.sampleTrackMetadata"
        tracks_metadata = self.b.find_elements_by_css_selector(sel)
        if relation == 'Was sampled':
            track_metadata = tracks_metadata[0]
        elif relation == 'Contains sample':
            track_metadata = tracks_metadata[1]
        sel = "div.sampleTrackArtists a"
        artist_a = track_metadata.find_element_by_css_selector(sel)
        artist_dict = {'name': artist_a.text,
                       'url': artist_a.get_attribute('href')}

        sel = "a.trackName"
        track = track_metadata.find_element_by_css_selector(sel)
        song_dict = {'name': track.text,
                     'url': track.get_attribute('href')}

        return artist_dict, song_dict

    

    def get(self, url):
        self.b.get(url)
        time.sleep(1)
        self._accept_cookies()


    def _next_page(self):

        sel = 'div.pagination span.next'
        next_button = self.b.find_element_by_css_selector(sel)
        a = next_button.find_element_by_css_selector('a')
        url = a.get_attribute('href')
        time.sleep(round(stats.uniform(1,3).rvs(),2))
        self.get(url)

    def _see_all(self, section_starts_with):

        sel = "div#content div.divided-layout\
         div.layout-container.leftContent\
         section \
         header.sectionHeader"
        sections = self.b.find_elements_by_css_selector(sel)

        for section in sections:
            if section.text.startswith(section_starts_with):
                current_section = section
        a = current_section.find_element_by_css_selector(
                'header.sectionHeader a.moreButton')
        url = a.get_attribute('href')
        print(url)
        self.get(url) 