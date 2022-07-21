import pandas
from backendAPI import API

csv = "./data/monthly_f35_weather_canx.csv"
#csv = "./data/monthly_global_hawk_weather_canx.csv"

def main():
    api = API(csv, useMemory = True, deleteExisting = True)
    connection = api.createDatabase()
    bases = api.getBases()
    for base in bases: print(base)
    connection.close()

if __name__ == "__main__":
    main()