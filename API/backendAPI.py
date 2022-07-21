import os
import csv
import sqlite3

class API:
    def __init__(self, csvFile, useMemory = False, deleteExisting = False):
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

    def getBases(self):
        self.__getBasesQuery = "SELECT DISTINCT base_text, latitude, longitude FROM " + self.__tableName
        self.__cursor.execute(self.__getBasesQuery)
        return self.__cursor.fetchall()
