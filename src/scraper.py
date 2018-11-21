
import selenium
from selenium.webdriver import Firefox, Chrome
import time

class Scraper():

    __init__(self, browser='Firefox()', url):
    self.b = browser
    self.start_url = url
    b.get(url)


    def _accept_cookies(self):
    try:
        button = self.b.find_element_by_css_selector('button.qc-cmp-button')
        button.click()
    except selenium.common.exceptions.NoSuchElementException:
        pass


        # desired_section = 'Most influential artists'
        # sel = "div#content div.divided-layout div.layout-container.leftContent div"

    def find_desired_section(self, sect_divs, desired_section):
        for i, div in enumerate(sect_divs):
            if div.text.startswith(desired_section):
                return sect_divs[i+1]

    def get_artist_urls(self, sect_divs, desired_section):
        artist_section = self.find_desired_section(sect_divs, desired_section)
        artist_tiles = artists_section.find_elements_by_css_selector('li')
        artists = {}
        for tile in artist_tiles:
            tile.location_once_scrolled_into_view
            time.sleep(2)
            a = tile.find_element_by_css_selector('a')
            artist_name = tile.text
            yield {'name': artist_name,
                    'url': a.get_attribute('href')}

