from config.databaseconfig import Databaseconfig
from config import databaseconfig as dbc


class Document:

    def __init__(self):
        connection = Databaseconfig()
        connection.connect()
        self.db = dbc.client ["OBD"]

    def obdDB_Write(self, data, col):
        parameter = data
        collection = self.db[col]
        # print(parameter,type(parameter))
        collection.insert_one(parameter)

    def obdDB_Read(self):
        v = self.collection.find()
        list = []
        for i in v:
            value = i
            list.append(value)
        # print(list)
        return list



