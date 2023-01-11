import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import requests

class htmlParser:
    @staticmethod
    def is_youtube_url(url):
        parsed_url = urlparse(url)
        return parsed_url.hostname in ['youtube.com', 'www.youtube.com']

    @staticmethod
    def get_youtube_externalId_by_tag(url):
        if not htmlParser.is_youtube_url(url):
            raise Exception("invalid youtube channel")
            
        html = requests.get(url, verify=False).text
        soup = BeautifulSoup(html, 'html.parser')
        channel_id = soup.select_one('meta[property="og:url"]')['content'].strip('/').split('/')[-1]

        return None