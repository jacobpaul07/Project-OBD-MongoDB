import datetime
import threading
from Utility import convert_raw_to_information,gps_one,gps_main
# import boto3
import pytz
import json

global_lock = threading.Lock()
stopThread: bool = False



class SocketThread(threading.Thread):
    def __init__(self,clientAddress,clientsocket,deviceCount):
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        self.clientAddress = clientAddress
        self.count = 0
        self.deviceCount = deviceCount
        self.gpslist_lat = []
        self.gpslist_lon = []
        print ("New connection added: ", clientAddress)

    def run(self):
       
        # cli = boto3.client('s3')
        while True:
            try:
                
                data = self.csocket.recv(1024)
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
                        atIMEI = "@"+IMEI
                        messageType = "00"
                        sequenceNumber = fData["Sequence No"]
                        checkSum = "*CS"
                        packet = atIMEI,messageType,sequenceNumber,checkSum
                        seperator = ","
                        joinedPacket = seperator.join(packet)
                        bytesPacket = bytes(joinedPacket, 'utf-8')
                        print("Return Packet:",bytesPacket)


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
                        self.csocket.send(bytesPacket)
                        print ("Client at", self.clientAddress , "Packet Completely Received...")
                    
                    else:
                        print(" 'H' data Received: ",data)

            except Exception as exception:
                print ("Error occured with exception:",exception)
            # print(self.count)
            print("--------------------------------------------------------------------------------------------")


         
        