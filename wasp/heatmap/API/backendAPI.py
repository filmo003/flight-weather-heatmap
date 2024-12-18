import os
import csv
import sqlite3
import pandas as pd
import numpy as np
from .aircrafts import Aircrafts


class API:
    def __init__(self, csvFile, useMemory=False, deleteExisting=False):
        self.__aircraftDataManager = Aircrafts()
        self.__tableName = "weatherData"
        self.__databaseFileName = self.__tableName + ".db"
        # self.__csvFile = "./example_data/KRDR_cleaned.csv"
        self.__csvFile = csvFile
        self.__exists = False

        if os.path.exists(self.__databaseFileName):
            self.__exists = True
            if deleteExisting:
                os.remove(self.__databaseFileName)
                self.__exists = False
                print("Existing database found. Successfully deleted")

        if useMemory:
            self.__connection = sqlite3.connect(":memory:", check_same_thread=False)
        else:
            self.__connection = sqlite3.connect(
                self.__databaseFileName, check_same_thread=False
            )
        self.__cursor = self.__connection.cursor()

    def __getHeaderTypes(self, file):
        self.__headerTypes = {}
        self.__reader = csv.DictReader(file)

        for self.__cell in self.__reader:
            # Insert headers if they do not already exist
            self.__headers = [
                f
                for f in self.__reader.fieldnames
                if f.lower().replace(" ", "_") not in self.__headerTypes.keys()
            ]
            if not self.__headers:
                break  # Exit if no headers
            for self.__field in self.__headers:
                self.__data = self.__cell[self.__field]

                if len(self.__data) == 0:
                    continue
                if self.__data.isdigit():
                    self.__headerTypes[self.__field.lower().replace(" ", "_")] = (
                        "INTEGER"
                    )
                else:
                    self.__headerTypes[self.__field.lower().replace(" ", "_")] = "TEXT"

        if len(self.__headers) > 0:
            raise Exception(
                "Failed to find all the columns data types - Maybe some are empty?"
            )
        return self.__headerTypes

    def __getEscapingGenerator(self, file):
        for line in file:
            yield line.encode("ascii", "xmlcharrefreplace").decode("ascii")

    def createDatabase(self):
        if not self.__exists:
            with open(self.__csvFile, mode="r", encoding="ISO-8859-1") as self.__file:
                self.__headerTypes = self.__getHeaderTypes(self.__file)
                self.__file.seek(0)

                self.__reader = csv.DictReader(self.__file)
                self.__headers = self.__reader.fieldnames
                self.__columns = []

                for self.__header in self.__headers:
                    self.__header = self.__header.lower().replace(" ", "_")
                    self.__columns.append(
                        "%s %s" % (self.__header, self.__headerTypes[self.__header])
                    )

                self.__createTableQuery = (
                    "CREATE TABLE "
                    + self.__tableName
                    + " (%s)" % ",".join(self.__columns)
                )
                self.__cursor.execute(self.__createTableQuery)

                self.__file.seek(0)
                self.__reader = csv.reader(self.__getEscapingGenerator(self.__file))

                self.__insertQuery = (
                    "INSERT INTO "
                    + self.__tableName
                    + " VALUES(%s);" % ",".join("?" * len(self.__columns))
                )
                self.__cursor.executemany(self.__insertQuery, self.__reader)

                self.__indexQuery = "CREATE INDEX bases_index ON weatherData (base_text, year, month, day, hour, air_temp, visibility, cross_wind_speed, wind_gust_speed, peak_wind_speed, ceiling_full, thunderstorms, freezing_rain, fog_haze, hail, icing_percent_low, icing_percent_med, icing_percent_high)"
                self.__cursor.execute(self.__indexQuery)

                self.__connection.commit()
        else:
            print("Database already exists.")
        return self.__connection

    def executeQuery(self, query):
        self.__cursor.execute(query)
        return self.__cursor.fetchall()

    def getBases(self):
        # self.__getBasesQuery = "SELECT DISTINCT base_text, latitude, longitude FROM " + self.__tableName
        # self.__df = pd.read_sql(self.__getBasesQuery, self.__connection)
        # self.__df = self.__df.loc[1:].reset_index(drop = True)
        # self.__df[["latitude", "longitude"]] = self.__df[["latitude", "longitude"]].astype("float")
        # return self.__df
        self.__getBasesQuery = (
            "SELECT DISTINCT base_text, latitude, longitude FROM " + self.__tableName
        )
        self.__df = pd.read_sql(self.__getBasesQuery, self.__connection)
        self.__df = self.__df.loc[1:].reset_index(drop=True)

        def safe_float(x):
            try:
                return float(x)
            except ValueError:
                return np.nan

        # Handle latitude/ longitude import errors from csv, drop if wrong
        self.__df["latitude"] = self.__df["latitude"].apply(safe_float)
        self.__df["longitude"] = self.__df["longitude"].apply(safe_float)

        self.__df = self.__df.dropna(subset=["latitude", "longitude"])
        self.__df = self.__df.reset_index(drop=True)
        return self.__df

    def getAircraftData(self, aircraft):
        return self.__aircraftDataManager.getData(aircraft)

    def getCanx(self, baseName, aircraft, month=False, daily=False):
        self.__aircraftData = self.__aircraftDataManager.getData(aircraft)
        self.__query = (
            "SELECT DISTINCT base_text, year, month, day, hour, air_temp, visibility, cross_wind_speed, wind_gust_speed, peak_wind_speed, ceiling_full, thunderstorms, freezing_rain, fog_haze, hail, icing_percent_low, icing_percent_med, icing_percent_high FROM "
            + self.__tableName
            + " WHERE base_text = "
            + "'"
            + baseName
            + "'"
        )
        self.__df = pd.read_sql(self.__query, self.__connection)
        self.__df[self.__df.columns[1:]] = self.__df[self.__df.columns[1:]].astype(
            "float"
        )
        if month:
            self.__df = self.__df[self.__df["month"] == month]
        self.__df["canx"] = 0
        self.__df["type"] = ""

        self.__df.loc[
            self.__df["air_temp"] > self.__aircraftData["highTemp"], "canx"
        ] = 1
        self.__df.loc[
            self.__df["air_temp"] < self.__aircraftData["lowTemp"], "canx"
        ] = 1
        self.__df.loc[
            self.__df["visibility"] < self.__aircraftData["visibility"], "canx"
        ] = 1
        self.__df.loc[
            self.__df["cross_wind_speed"] > self.__aircraftData["crosswind"], "canx"
        ] = 1
        self.__df.loc[
            self.__df["wind_gust_speed"] > self.__aircraftData["windGust"], "canx"
        ] = 1
        self.__df.loc[
            self.__df["peak_wind_speed"] > self.__aircraftData["maxwind"], "canx"
        ] = 1
        self.__df.loc[
            self.__df["ceiling_full"] < self.__aircraftData["ceiling"], "canx"
        ] = 1
        if self.__aircraftData["thunderstorm"]:
            self.__df.loc[self.__df["thunderstorms"] == 1, "canx"] = 1
        if self.__aircraftData["freezingRain"]:
            self.__df.loc[self.__df["freezing_rain"] == 1, "canx"] = 1
        if self.__aircraftData["fog"]:
            self.__df.loc[self.__df["fog_haze"] == 1, "canx"] = 1
        if self.__aircraftData["hail"]:
            self.__df.loc[self.__df["hail"] == 1, "canx"] = 1
        if self.__aircraftData["thunderstorm"]:
            self.__df.loc[self.__df["thunderstorms"] == 1, "canx"] = 1

        self.__df.loc[
            self.__df["icing_percent_" + self.__aircraftData["icing"]] > 0.5, "canx"
        ] = 1

        self.__middle = self.__aircraftData["takeoffWindow"] // 2
        self.__low = self.__aircraftData["takeoffTime"] - self.__middle
        self.__high = (
            self.__aircraftData["takeoffTime"]
            + self.__aircraftData["takeoffWindow"]
            - self.__middle
        )

        self.__df.loc[
            (self.__df["hour"] >= self.__low) & (self.__df["hour"] <= self.__high),
            "type",
        ] = "takeoff"

        self.__middle = self.__aircraftData["landingWindow"] // 2
        self.__low = self.__aircraftData["landingTime"] - self.__middle
        self.__high = (
            self.__aircraftData["landingTime"]
            + self.__aircraftData["landingWindow"]
            - self.__middle
        )

        self.__df.loc[
            (self.__df["hour"] >= self.__low) & (self.__df["hour"] <= self.__high),
            "type",
        ] = "landing"
        self.__df = self.__df[self.__df["type"] != ""]

        self.__df = (
            self.__df.groupby(["type", "year", "month", "day"]).min().reset_index()
        )
        self.__df = self.__df.groupby(["year", "month", "day"]).max().reset_index()
        if daily:
            self.__df = self.__df.select_dtypes(include=["number"])
            self.__df = self.__df.groupby(["month", "day"]).mean().reset_index()
            return self.__df[["month", "day", "canx"]]
        else:
            self.__df = self.__df.select_dtypes(include=["number"])
            self.__df = self.__df.groupby(["month"]).mean().reset_index()
            print("MONTHS")
            print(self.__df.iloc[0])

            if month:
                return self.__df["canx"][0]
            else:
                return self.__df[["month", "canx"]]
