from urllib.parse import urljoin
from fe.access.auth import Auth
import requests

class Search:
    def __init__(self, url_prefix):
        self.url_prefix = urljoin(url_prefix, "search/")

    def search_info(self, page_id : int, store_id : str, info: dict) -> int:
        url = urljoin(self.url_prefix, "search")
        json = {
            "page_id":page_id,
            "store_id":store_id,
            "search_info":info
        }
        r = requests.post(url, json=json)
        return r.status_code
