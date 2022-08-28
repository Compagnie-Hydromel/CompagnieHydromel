import mysql.connector, csv

def dbConnector():
    # use DB credentials
    with open('lib/credentials', 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            return mysql.connector.connect(
              host=row[0],
              port=row[1],
              user=row[2],
              password=row[3],
              database=row[4]
            )

def querySelect(query):
    database = dbConnector()

    Cursor = database.cursor()

    Cursor.execute(query)

    return Cursor.fetchall()

def queryInsert(query):
    database = dbConnector()

    Cursor = database.cursor()

    Cursor.execute(query)

    database.commit()

    return Cursor.rowcount
