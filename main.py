from PvScraper import scrape
from PvScraper import webserver

Scraper = scrape.Scraper("192.168.178.31")

Scraper.get_onto_website()

Webserver = webserver.WebServer(Scraper)