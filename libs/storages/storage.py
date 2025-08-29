from io import BytesIO
from io import IOBase
import re


class Storage:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Storage, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def get(self, url, return_type=bytes):
        match_group = self.__check_format(url)
        storage_instance = self.__get_storage_instance(match_group[0])
        return self.__return_data_morphing(storage_instance.get(match_group[1]), return_type)

    def get_path(self, url) -> str:
        match_group = self.__check_format(url)
        storage_instance = self.__get_storage_instance(match_group[0])
        return storage_instance.get_path(match_group[1])

    def get_file_type(self, url) -> str:
        match_group = self.__check_format(url)
        storage_instance = self.__get_storage_instance(match_group[0])
        return storage_instance.get_file_type(match_group[1])

    def put(self, file, filename: str = None) -> str:
        match_group = self.__check_format(filename)
        storage_instance = self.__get_storage_instance(match_group[0])
        return storage_instance.put(self.__data_morphing(file), match_group[1])

    def delete(self, url: str) -> bool:
        match_group = self.__check_format(url)
        storage_instance = self.__get_storage_instance(match_group[0])
        return storage_instance.delete(match_group[1])

    def __check_format(self, url: str) -> str:
        pattern = r"^([a-z]{0,}):\/\/([a-zA-Z\/. éàè,-_!~]{1,})$"
        match = re.match(pattern, url)
        if match:
            return match.groups()
        raise ValueError(f"Unsupported URL format: {url}")

    def __get_storage_instance(self, storage_type: str):
        match storage_type:
            case "local":
                from libs.storages.local_storage import LocalStorage
                return LocalStorage("storages/locals")
            case "caches":
                from libs.storages.local_storage import LocalStorage
                return LocalStorage("storages/caches")
            case "http" | "https":
                from libs.storages.https_storage import HTTPSStorage
                return HTTPSStorage(storage_type + "://")
            case _:
                raise ValueError(f"Unsupported storage type: {storage_type}")

    def __data_morphing(self, data):
        if isinstance(data, BytesIO):
            data.seek(0)
            return data.read()
        elif isinstance(data, bytes):
            return data
        elif isinstance(data, str):
            with open(data, 'rb') as file:
                return file.read()
        raise ValueError("Data must be a BytesIO or a file path string.")

    def __return_data_morphing(self, data, return_type):
        if return_type == bytes:
            return data
        elif return_type == BytesIO:
            return BytesIO(data)
        elif return_type == IOBase:
            bio = BytesIO(data)
            bio.seek(0)
            return bio
        elif return_type == str:
            return data.decode('utf-8')
        raise ValueError("Return type must be bytes or BytesIO.")
