import requests
from urllib.parse import urlsplit
from posixpath import splitext

from libs.exception.storage.cant_store_file_with_https_exception import CantStoreFileWithHTTPSException


class HTTPSStorage:
    def __init__(self, prefix: str):
        self.prefix = prefix

    def get(self, url):
        response = requests.get(self.prefix + url)
        response.raise_for_status()
        return response.content

    def get_path(self, url) -> str:
        return self.prefix + url

    def get_file_type(self, url) -> str:
        return splitext(urlsplit(self.prefix + url).path)[1].lstrip('.').lower()

    def put(self, data, key):
        raise CantStoreFileWithHTTPSException(
            "Cannot store files using HTTPS storage.")

    def delete(self, url):
        response = requests.delete(self.prefix + url)
        response.raise_for_status()
        return response
