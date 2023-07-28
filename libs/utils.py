import os

class Utils():
    """This class is designed to manage the utils.
    """
    def createDirectoryIfNotExist(self, directory:str):
        """This method is designed to create a directory if not exist.

        Args:
            directory (str): The directory to create. (example: "path/to/directory")
        """
        if not os.path.exists(directory):
            os.mkdir(directory)