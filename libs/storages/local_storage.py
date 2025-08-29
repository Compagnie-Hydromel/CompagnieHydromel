import os
import json

from libs.utils.utils import Utils


class LocalStorage:
    def __init__(self, storage_dir):
        self.storage_dir = storage_dir
        Utils.createDirectoryIfNotExist(storage_dir)

    def _get_file_path(self, key):
        return os.path.join(self.storage_dir, key)

    def get(self, key):
        file_path = self._get_file_path(key)
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'rb') as file:
            return file.read()

    def get_path(self, key) -> str:
        return self._get_file_path(key)

    def get_file_type(self, key) -> str:
        _, ext = os.path.splitext(key)
        return ext.lstrip('.').lower()

    def put(self, data, key):
        file_path = self._get_file_path(key)
        Utils.createDirectoryIfNotExist(os.path.dirname(file_path))
        with open(file_path, 'wb') as file:
            file.write(data)
        return key

    def delete(self, key):
        file_path = self._get_file_path(key)
        if os.path.exists(file_path):
            os.remove(file_path)
