import selenium
from selenium.webdriver import Firefox, Chrome
import time
import pandas as pd
from scipy import stats 
import urllib.parse

class Scraper():
    """A web scraper specific to https://www.whosampled.com"""

    def __init__(self, browser=None):
        if browser is None:
            self.b = Firefox(timeout=60)
        else:
            self.b = browser


    def _accept_cookies(self):
        """Finds 'Accept Cookies' Button if it exists and clicks"""
        try:
            button = self.b.find_element_by_css_selector('button.qc-cmp-button')
            button.click()
        except (selenium.common.exceptions.NoSuchElementException,
                selenium.common.exceptions.ElementNotInteractableException):
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
        time.sleep(3)
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
        self.get(artist_url_dict['url'])
        self._accept_cookies()
        self._choose_artist_role_as_artist()
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
                'name': track.text,
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
        page = self._see_all('Was sampled in')
        last_page = False
        while last_page == False:
            self._get_samples_inferred_url(sampled_in_song_list, artist_list, 'Was sampled')
            try:
                page = self._next_page()
            except selenium.common.exceptions.NoSuchElementException:
                last_page = True
        
        if page != 'See all button does not exist':
            self.get(song_url)

        # samples
        page = self._see_all('Contains sample')
        last_page = False
        while last_page == False:
            self._get_samples_inferred_url(samples_song_list, artist_list, 'Contains sample')
            try:
                page = self._next_page()
            except selenium.common.exceptions.NoSuchElementException:
                last_page = True

        return sampled_in_song_list, samples_song_list, artist_list


    def _get_samples(self, sampled_in_song_list, artist_list, relation):

        sample_urls = []
        sel = "div#content\
               div.divided-layout\
               div.layout-container.leftContent\
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
        try:
            song_sections = current_section.find_elements_by_css_selector(sel)
        except AttributeError:
            return None
        
        for song in song_sections:
            a = song.find_element_by_css_selector('a')
            sample_urls.append(a.get_attribute('href'))
            print(sample_urls)

        for sample in sample_urls:
            artist_dict, song_dict = (
                self._get_metadata_from_sample_page(sample, relation))
            artist_list.append(artist_dict)
            sampled_in_song_list.append(song_dict)
            print(song_dict)

            

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
        artist_url = artist_a.get_attribute('href')
        artist_dict = {'name': artist_a.text,
                       'url': artist_a.get_attribute('href')}

        sel = "a.trackName"
        track = track_metadata.find_element_by_css_selector(sel)
        song_dict = {'name': track.text,
                     'url': track.get_attribute('href'),
                     'artist_url': artist_url,
                     'artist_id': None}

        return artist_dict, song_dict

    

    def get(self, url):
        self.b.get(url)
        self._accept_cookies()
        print(url)


    def _next_page(self):

        sel = 'div.pagination span.next'
        next_button = self.b.find_element_by_css_selector(sel)
        a = next_button.find_element_by_css_selector('a')
        url = a.get_attribute('href')
        time.sleep(round(stats.uniform(1,3).rvs(),2))
        self.get(url)
        return url

    def _see_all(self, section_starts_with):

        try:
            sel = "div#content div.divided-layout\
            div.layout-container.leftContent\
            section \
            header.sectionHeader"
            sections = self.b.find_elements_by_css_selector(sel)

            for section in sections:
                if section.text.startswith(section_starts_with):
                    current_section = section
            a = current_section.find_element_by_css_selector('a.moreButton')
            url = a.get_attribute('href')
            self.get(url) 
            return url
        except (UnboundLocalError,
                selenium.common.exceptions.NoSuchElementException):
            return 'See all button does not exist'

    def _get_samples_inferred_url(self, song_list, artist_list, relation):

        sel = "div#content\
            div.divided-layout\
            div.layout-container.leftContent\
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
        
        try:
            sel = "div.listEntry.sampleEntry"
            song_sections = current_section.find_elements_by_css_selector(sel)
            for song in song_sections:
                song_details = song.find_element_by_css_selector('div.details-inner')
                
                artist_details = song_details.find_element_by_css_selector('span.trackArtist')
                artist_a = artist_details.find_element_by_css_selector('a')
                artist_url = artist_a.get_attribute('href')
                artist_dict = {'name': artist_a.text,
                                'url': artist_a.get_attribute('href')}
                song_name = (song_details
                                .find_element_by_css_selector('a.trackName')
                                .text)
                song_url = artist_url + urllib.parse.quote(song_name.replace(' ', '-')) + '/'
                song_dict = {'name': song_name,
                                'url': song_url,
                                'artist_url': artist_url,
                                'artist_id': None}

                artist_list.append(artist_dict)
                song_list.append(song_dict)
                


        except AttributeError:
            return None
            print('fjds;afjds;ah')

    def _choose_artist_role_as_artist(self):
        try:
            sel = 'div.optionMenu.artist-role'
            role_selector = self.b.find_element_by_css_selector(sel)
            roles = role_selector.find_elements_by_css_selector('li')

            for role in roles:
                try:
                    a = role.find_element_by_css_selector('a')
                    if a.get_attribute('innerHTML') == 'As an Artist':
                        url = a.get_attribute('href')
                    else:
                        continue
                except selenium.common.exceptions.NoSuchElementException:
                    continue
            self.get(url)
        except (selenium.common.exceptions.NoSuchElementException,
                UnboundLocalError):
            pass
