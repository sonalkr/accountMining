import sqlite3


def getDb():
    connection = sqlite3.connect('data.sqlite')
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def getDgReadOnly():
    connection = sqlite3.connect('data.sqlite', uri=True)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection



def getDbWithDictionary():
    connection = sqlite3.connect('data.sqlite')
    connection.execute("PRAGMA foreign_keys = ON")
    connection.row_factory = sqlite3.Row
    return connection
    