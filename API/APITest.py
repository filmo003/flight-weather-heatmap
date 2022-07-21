import pandas
from backendAPI import API

csv = "./data/example_data/example_data.csv"
#csv = "./data/monthly_f35_weather_canx.csv"
#csv = "./data/monthly_global_hawk_weather_canx.csv"

def main():
    api = API(csv, useMemory = False, deleteExisting = False)
    connection = api.createDatabase()

    #This is how you get Canx data for a specific base and aircraft. Returns {Name, Month, Canx}
    canx = api.getCanx("BEALE AFB", "global-Hawk")
    #for canx in canx: print(canx)

    #This is how you get DEV Canx data for a specific base. Returns {Name, Month, Canx}
    # canx = api.getDEVCanx("BEALE AFB")
    # for canx in canx: print(canx)

    #This is how you can query all base info. Returns {Name, Latitude, Longitude}
    #bases = api.getBases()
    #for base in bases: print(bases)

    #This is how you can create your own custom query. Returns all results
    # custom = api.executeQuery("SELECT * FROM weatherData")
    # print(custom)

    connection.close()

if __name__ == "__main__":
    main()