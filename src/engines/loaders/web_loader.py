import requests
import logging

class WebLoader:
    def __init__(self, logger: logging.Logger, url: str):
        self.url = url
        self.logger = logger

    def request(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            return response.text
        else:
            self.logger.error(f"Error fetching data: {response.status_code}")
            return None