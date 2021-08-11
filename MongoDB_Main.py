from config.databaseconfig import Databaseconfig
from config import databaseconfig as dbc
import json
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
        newvalues = { "$set": { "Device_Status":status} }
        x = collection.update_one(myquery, newvalues)
        updatedCount = x.matched_count
        # print(updatedCount, "documents updated.")
        return updatedCount
    
    def obd_RPM(self,col,IMEI,rpm):
        collection = self.db[col]
        myquery = { "IMEI": IMEI }
        newvalues = { "$set": { "Rpm":rpm} }
        x = collection.update_one(myquery, newvalues)
        updatedCount = x.matched_count
        return updatedCount
    
    def obdDeviceStatusDocument(self,col,IMEI,Latitude,NoS,Longitude,EoW,batLevel,SignalStrength):
        collection = self.db[col]
        myquery = { "IMEI": IMEI }
        newvalues = { "$set": {
            "Latitude": Latitude,
            "North_South": NoS,
            "Longitude": Longitude,
            "East_West": EoW,
            "Internal_battery_Level": batLevel,
            "Signal_Strength": SignalStrength,
            } 
        }
        x = collection.update_one(myquery, newvalues)
        updatedCount = x.matched_count
        # print(updatedCount, "documents updated.")
        return updatedCount

    def obdRead_Document(self,col,IMEI):
        collection = self.db[col]
        myquery = { "IMEI": IMEI }
        x = collection.find_one(myquery)
        # print(updatedCount, "documents updated.")
        return x

# col = "OBD_Device_Status"
# IMEI = "866039048578802"
# b=(Document().obdDB_Read(col)[0])
# a = json.dumps(b,default = str)
# print(type(a))

# from mongoengine import Document, ListField, StringField, URLField

# class Tutorial(Document):
#     title = StringField(required=True, max_length=70)
#     author = StringField(required=True, max_length=20)
#     contributors = ListField(StringField(max_length=20))
#     url = URLField(required=True)

# def tutorial():
#     tutorial1 = Tutorial(
#     title="Beautiful Soup: Build a Web Scraper With Python",
#     author="Martin",
#     contributors=["Aldren", "Geir Arne", "Jaya", "Joanna", "Mike"],
#     url="https://realpython.com/beautiful-soup-web-scraper-python/"
# )

# tutorial1.save()  # Insert the new tutorial