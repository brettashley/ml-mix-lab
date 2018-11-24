import selenium
from selenium.webdriver import Firefox, Chrome
import time

class Scraper():

    def __init__(self, url, browser=Firefox()):
        self.b = browser
        self.start_url = url
        self.b.get(self.start_url)


    def _accept_cookies(self):
        try:
            button = self.b.find_element_by_css_selector('button.qc-cmp-button')
            button.click()
        except selenium.common.exceptions.NoSuchElementException:
            pass


        # desired_section = 'Most influential artists'
        # sel = "div#content div.divided-layout div.layout-container.leftContent div"

    def find_desired_section(self, sel, desired_section):
        self._accept_cookies()
        sect_divs = self.b.find_elements_by_css_selector(sel)
        for i, div in enumerate(sect_divs):
            if div.text.startswith(desired_section):
                return sect_divs[i+1]

    def get_artist_urls(self, artists_section):
        artist_tiles = artists_section.find_elements_by_css_selector('li')
        artists = {}
        for tile in artist_tiles:
            tile.location_once_scrolled_into_view
            time.sleep(2)
            a = tile.find_element_by_css_selector('a')
            artist_name = tile.text
            yield {'name': artist_name,
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
