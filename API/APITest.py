import pandas
from backendAPI import API

csv = "./data/monthly_f35_weather_canx.csv"
#csv = "./data/monthly_global_hawk_weather_canx.csv"

def main():
    api = API(csv, useMemory = False, deleteExisting = False)
    connection = api.createDatabase()

    #This is how you cet Canx data for a specific base. Returns {Name, Month, Canx}
    canx = api.getCanx("EGLIN AFB")
    for canx in canx: print(canx)

    #This is how you can query all base info. Returns {Name, Latitude, Longitude}
    # bases = api.getBases()
    # for base in bases: print(base)

    #This is how you can create your own custom query. Returns all results
    # custom = api.executeQuery("SELECT * FROM weatherData")
    # print(custom)

    connection.close()

if __name__ == "__main__":
    main()