import selenium
from selenium.webdriver import Firefox, Chrome
import time
from scraper import Scraper


sel = "div#content div.divided-layout div.layout-container.leftContent div"
url = 'https://www.whosampled.com/genre/Soul-Funk-Disco/'
desired_section = 'Most influential artists'

s = Scraper(url)
artist_section = s.find_desired_section(sel, desired_section)

