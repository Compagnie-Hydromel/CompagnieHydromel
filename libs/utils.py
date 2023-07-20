import os

class Utils():
    def createDirectoryIfNotExist(self, directory:str):
        if not os.path.exists(directory):
            os.mkdir(directory)