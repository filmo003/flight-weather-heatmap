import os
import csv
import sqlite3
import pandas as pd
from .aircrafts import Aircrafts

class API:
    def __init__(self, csvFile, useMemory = False, deleteExisting = False):
        self.__aircraftDataManager = Aircrafts()
        self.__tableName = "weatherData"
        self.__databaseFileName = self.__tableName + ".db"
        #self.__csvFile = "./example_data/KRDR_cleaned.csv"
        self.__csvFile = csvFile
        self.__exists = False

        if os.path.exists(self.__databaseFileName):
            self.__exists = True
            if(deleteExisting):
                os.remove(self.__databaseFileName)
                self.__exists = False
                print("Existing database found. Successfully deleted")

        if(useMemory):
            self.__connection = sqlite3.connect(":memory:")
        else:
            self.__connection = sqlite3.connect(self.__databaseFileName)
        self.__cursor = self.__connection.cursor()
    

    def __getHeaderTypes(self, file):
        self.__headerTypes = {}
        self.__reader = csv.DictReader(file)

        for self.__cell in self.__reader:
            #Insert headers if they do not already exist
            self.__headers = [f for f in self.__reader.fieldnames if f.lower().replace(" ", "_") not in self.__headerTypes.keys()]
            if not self.__headers: break #Exit if no headers
            for self.__field in self.__headers:
                self.__data = self.__cell[self.__field]

                if len(self.__data) == 0:
                    continue
                if self.__data.isdigit():
                    self.__headerTypes[self.__field.lower().replace(" ", "_")] = "INTEGER"
                else:
                    self.__headerTypes[self.__field.lower().replace(" ", "_")] = "TEXT"
        
        if len(self.__headers) > 0:
            raise Exception("Failed to find all the columns data types - Maybe some are empty?")
        return self.__headerTypes

    
    def __getEscapingGenerator(self, file):
        for line in file:
            yield line.encode("ascii", "xmlcharrefreplace").decode("ascii")


    def createDatabase(self):
        if (not self.__exists):
            with open(self.__csvFile, mode = "r", encoding = "ISO-8859-1") as self.__file:
                self.__headerTypes = self.__getHeaderTypes(self.__file)
                self.__file.seek(0)

                self.__reader = csv.DictReader(self.__file)
                self.__headers = self.__reader.fieldnames
                self.__columns = []

                for self.__header in self.__headers:
                    self.__header = self.__header.lower().replace(" ", "_")
                    self.__columns.append("%s %s" % (self.__header, self.__headerTypes[self.__header]))
                
                self.__createTableQuery = "CREATE TABLE " + self.__tableName + " (%s)" % ",".join(self.__columns)
                self.__cursor.execute(self.__createTableQuery)
                
                self.__file.seek(0)
                self.__reader = csv.reader(self.__getEscapingGenerator(self.__file))

                self.__insertQuery = "INSERT INTO " + self.__tableName + " VALUES(%s);" % ','.join('?' * len(self.__columns))
                self.__cursor.executemany(self.__insertQuery, self.__reader)
                self.__connection.commit()
        else:
            print("Database already exists.")
        return self.__connection
    
    def executeQuery(self, query):
        self.__cursor.execute(query)
        return self.__cursor.fetchall()

    def getBases(self):
        self.__getBasesQuery = "SELECT DISTINCT base_text, latitude, longitude FROM " + self.__tableName
        self.__cursor.execute(self.__getBasesQuery)
        self.__values = self.__cursor.fetchall()
        for i in range(1, len(self.__values)):
            values = self.__values[i][0], float(self.__values[i][1]), float(self.__values[i][2])
        return values

    def getDEVCanx(self, baseName):
        self.__getCanxQuery = "SELECT DISTINCT base_text, Month, canx FROM " + self.__tableName +" WHERE base_text = " + "'" + baseName + "'"
        self.__cursor.execute(self.__getCanxQuery)
        self.__values = self.__cursor.fetchall()
        for i in range(1, len(self.__values)):
            values = self.__values[i][0], float(self.__values[i][1]), float(self.__values[i][2])
        return values
    
    def getAircraftData(self, aircraft):
        return self.__aircraftDataManager.getData()

    def getCanx(self, baseName, aircraft):
        # self.__hail = []
        # self.__fog_haze = []
        # self.__air_temp = []
        # self.__canxValues = []
        # self.__visibility = []
        # self.__ceiling_full = []
        # self.__thunderstorms = []
        # self.__freezing_rain = []
        # self.__wind_gust_speed = []
        # self.__peak_wind_speed = []
        # self.__cross_wind_speed = []
        # self.__icing_percent_low = []
        # self.__icing_percent_med = []
        # self.__icing_percent_high = []
        self.__aircraftData = self.__aircraftDataManager.getData(aircraft)
        self.__query = "SELECT DISTINCT base_text, air_temp, visibility, cross_wind_speed, wind_gust_speed, peak_wind_speed, ceiling_full, thunderstorms, freezing_rain, fog_haze, hail, icing_percent_low, icing_percent_med, icing_percent_high FROM " + self.__tableName + " WHERE base_text = " + "'" + baseName + "'"
        self.__query2 = pd.read_sql(self.__query, self.__connection)
        self.__df = pd.DataFrame(self.__query2, columns = ["air_temp", "visibility", "cross_wind_speed", "wind_gust_speed", "peak_wind_speed", "ceiling_full", "thunderstorms", "freezing_rain", "fog_haze", "hail", "icing_percent_low", "icing_percent_med", "icing_percent_hig"])
        #self.__results = self.__cursor.execute(self.__query)
        #self.__queryValues = self.__results.fetchall()
        
        # for entry in self.__queryValues:
        #     self.__air_temp.append(float(entry[1]))
        #     self.__visibility.append(float(entry[2]))
        #     self.__cross_wind_speed.append(float(entry[3]))
        #     self.__wind_gust_speed.append(float(entry[4]))
        #     self.__peak_wind_speed.append(float(entry[5]))
        #     self.__ceiling_full.append(float(entry[6]))
        #     self.__thunderstorms.append(float(entry[7]))
        #     self.__freezing_rain.append(float(entry[8]))
        #     self.__fog_haze.append(float(entry[9]))
        #     self.__hail.append(float(entry[10]))
        #     self.__icing_percent_low.append(float(entry[11]))
        #     self.__icing_percent_med.append(float(entry[12]))
        #     self.__icing_percent_high.append(float(entry[13]))
        #     print(entry)
        
        # #True means you CAN fly Fasle means you CANNOT
        # self.__canxValues.append(False if max(self.__air_temp) > float(self.__aircraftData['highTemp']) else True)
        # self.__canxValues.append(False if min(self.__air_temp) < float(self.__aircraftData['lowTemp']) else True)
        # self.__canxValues.append(False if max(self.__visibility) < float(self.__aircraftData['visibility']) else True)
        # self.__canxValues.append(False if max(self.__cross_wind_speed) > float(self.__aircraftData['crosswind']) else True)
        # self.__canxValues.append(False if max(self.__wind_gust_speed) > float(self.__aircraftData['windGust']) else True)
        # self.__canxValues.append(False if max(self.__peak_wind_speed) > float(self.__aircraftData['maxwind']) else True)
        # self.__canxValues.append(False if max(self.__ceiling_full) < float(self.__aircraftData['ceiling']) else True)
        # self.__canxValues.append(False if max(self.__thunderstorms) == float(self.__aircraftData['thunderstorm'])else True)
        # self.__canxValues.append(False if max(self.__freezing_rain) == float(self.__aircraftData['freezingRain']) else True)
        # self.__canxValues.append(False if max(self.__fog_haze) == float(self.__aircraftData['fog']) else True)
        # self.__canxValues.append(False if max(self.__hail) == float(self.__aircraftData['hail']) else True)

        #print(self.__canxValues)

        # for index, entry in enumerate(self.__results.fetchall()):
        #     if index < 16:
        #         print(entry[index + 1])
        #         #print(list(self.__aircraftData.items())[index][1])
        #         self.__canxValues.append(False if float(entry[index + 1]) > int(list(self.__aircraftData.items())[index][1]) else True)
        return self.__cursor.fetchall()
        

