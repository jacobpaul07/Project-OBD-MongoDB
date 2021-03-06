import datetime
from socket import socket , timeout
import threading
from Utility import convert_raw_to_information,gps_one,gps_main
# import boto3
import pytz
import json
from MongoDB_Main import Document 

global_lock = threading.Lock()
stopThread: bool = False
doc = Document()


class SocketThread(threading.Thread):
    def __init__(self,clientAddress:str ,clientsocket:socket,deviceCount:int):
        threading.Thread.__init__(self)
        
        self.csocket = clientsocket
        self.clientAddress = clientAddress
        self.timeout = 300
        self.count = 0
        self.deviceCount = deviceCount
        self.gpslist_lat = []
        self.gpslist_lon = []
        self.maxRetryCount = 4
        self.currentRetryCount = 0
        setTimeout:int = self.timeout / self.maxRetryCount
        clientsocket.settimeout(setTimeout)
        print ("New connection added: ", clientAddress)

    def run(self):
        self.start = True
        # cli = boto3.client('s3')
        while self.start:
            try:
                data = self.csocket.recv(1024)
                print(data)  
                self.currentRetryCount = 0

                if not data:
                    return

                with global_lock:
                    IST = pytz.timezone('Asia/Kolkata') 
                    dateTimeIND = datetime.datetime.now(IST).strftime("%Y-%m-%dT%H:%M:%S.%f")
                    fData = convert_raw_to_information(data)

                    if fData["Live/Memory"] == "L":
                        print("TimeStamp: ", dateTimeIND)
                        print ("Connection from : ", self.clientAddress)
                        print('device number : ' , self.deviceCount)
                        print('thread identity:{0}'.format(str(threading.get_ident())))
                        print("Live Data: ",data)     

                        IMEI = fData["IMEI"]
                        # atIMEI = "@"+IMEI
                        # messageType = "00"
                        # sequenceNumber = fData["Sequence No"]
                        # checkSum = "*CS"
                        # packet = atIMEI,messageType,sequenceNumber,checkSum
                        # seperator = ","
                        # joinedPacket = seperator.join(packet)
                        # bytesPacket = bytes(joinedPacket, 'utf-8')
                        # print("Return Packet:",bytesPacket)

                        if fData["Message Type"] == "02" and fData["Live/Memory"] == "L":
                            lat = fData["Latitude"]
                            lon = fData["Longitude"]
                            if self.count == 0:
                                if lat == "":
                                    print("No Lat Lon available")
                                else:
                                    self.gpslist_lat.insert(0,lat)
                                    self.gpslist_lon.insert(0,lon)
                                    coordinates = {'Latitude' : lat, 'Longitude' : lon,'IMEI': IMEI, 'timestamp' : dateTimeIND} 
                                    self.count += 1
                                    # cli.put_object(
                                    #     Body=str(coordinates),
                                    #     Bucket='ec2-obd2-bucket',
                                    #     Key='{0}/Data/{0}_lat_lon_initial.txt'.format(IMEI))

                                    gps_one(lat, lon)
                                    print("initial:",self.gpslist_lat[0],self.gpslist_lon[0])
                            else:    
                                coordinates = {'Latitude' : lat, 'Longitude' : lon, 'IMEI':IMEI, 'timestamp' : dateTimeIND }
                                
                                # cli.put_object(
                                #     Body=str(coordinates),
                                #     Bucket='ec2-obd2-bucket',
                                #     Key='{0}/Data/{0}_lat_lon.txt'.format(IMEI))
                                # gps_main(self.gpslist_lat[0],self.gpslist_lon[0],lat,lon)

                                print("initial:",self.gpslist_lat[0],self.gpslist_lon[0])
                                print("live: ",lat,lon)
                        
                        elif fData["Message Type"] == "06" and fData["Live/Memory"] == "L":
                            print("Device Removed from the Vehical")
                            col = "OBD_Device_Status"
                            Plug:str = "FALSE"
                            doc.obd_Plugedin_Status(col,IMEI,Plug,dateTimeIND)
                        # self.csocket.send(bytesPacket)
                        # print ("Client at", self.clientAddress , "Packet Completely Received...")
                    
                    else:
                        print(" 'H' data Received: ")
                    
                    IMEI = fData["IMEI"]
                    atIMEI = "@"+IMEI
                    messageType = "00"
                    sequenceNumber = fData["Sequence No"]
                    checkSum = "*CS"
                    packet = atIMEI,messageType,sequenceNumber,checkSum
                    seperator = ","
                    joinedPacket = seperator.join(packet)
                    bytesPacket = bytes(joinedPacket, 'utf-8')
                    print("Return Packet:",bytesPacket)
                    self.csocket.send(bytesPacket)
                    print ("Client at", self.clientAddress , "Packet Completely Received...")
            
            except timeout as  exception:
                print("Timeout raised and caught.",exception)
                self.currentRetryCount = self.currentRetryCount + 1
                col = "OBD_Device_Status"
                colHistory = "OBD_Device_Status_History"
                if self.currentRetryCount > self.maxRetryCount:
                    status:str = "OFF"
                    print("Device",status)
                    doc.obd_Status(col,IMEI,status,dateTimeIND)
                    doc.obd_Status(colHistory,IMEI,status,dateTimeIND)
                    self.csocket.close()
                    self.start = False
                    self.currentRetryCount = 0
                else:
                    status:str = "IDLE"
                    print("Device",status)
                    RPM:str = "0"
                    doc.obd_RPM(col,IMEI,RPM,dateTimeIND)
                    doc.obd_Status(col,IMEI,status,dateTimeIND)
                    doc.obd_Status(colHistory,IMEI,status,dateTimeIND)
 
            except Exception as exception:
                print ("Error occured with exception:",exception)    
            
            print("--------------------------------------------------------------------------------------------")
      

# {"_id": {"$oid": "611377d37268d69df528d4c2"}, "Live/Memory": "L", "Signature": "ATL", "IMEI": "866039048578802", "Message Type": "06", "Sequence No": "7087", "Time (GMT)": "071005", "Date": "110821", "valid/invalid": "V", "Latitude": "", "Longitude": "", "Speed (knots)": "", "Angle of motion": "", "Odometer (KM)": "20.83",
#  "Internal battery Level (Volts)": "4.2", "Signal Strength": "17", "Mobile country code": "404", "Mobile network code": "40", "Cell id": "1b73", "Location area code": "116f", "#Ignition(0/1), RESERVED ,Harsh Braking / Acceleration//Non(0/2/3),Main power status(0/1)": "#1031", "Over speeding": "0", "CHECKSUM": "*$"}
