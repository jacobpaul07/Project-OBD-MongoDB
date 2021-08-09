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
        collection.insert_one(parameter)

    def obdDB_Read(self,col):
        collection = self.db[col]
        v = collection.find()
        list = []
        for i in v:
            value = i
            list.append(value)
        print(list)
        return list

    def obd_Status(self,col,IMEI,status):
        collection = self.db[col]
        myquery = { "IMEI": IMEI }
        newvalues = { "$set": { "Device Status":status} }
        x = collection.update_many(myquery, newvalues)
        updatedCount = x.matched_count
        # print(updatedCount, "documents updated.")
        return updatedCount

