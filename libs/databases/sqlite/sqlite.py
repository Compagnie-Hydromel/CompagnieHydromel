import sqlite3

class Sqlite():
    __db : sqlite3.Connection

    def __init__(self, file):
        self.__db =  sqlite3.connect(file)

    def select(self, query:str) -> dict:
        """This method is designed to execute a SQL SELECT query.

        Args:
            query (str): The SQL query

        Returns:
            dict: A dict with the informations who were fetch on the database.
        """

        cursor = self.__db.cursor()
        cursor.execute(query)

        result = cursor.fetchall()

        return result

    def modify(self, query:str) -> None:
        """This method is designed to execute a SQL query (Insert or Update).

        Args:
            query (str): The SQL query
        """

        cursor = self.__db.cursor()
        cursor.execute(query)

        self.__db.commit()

