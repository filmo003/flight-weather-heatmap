import pandas
from backendAPI import API

csv = "./example_data/output.csv"
#csv = "./example_data/newestData.csv"
#csv = "./example_data/KRDR_cleaned.csv"

def main():
    api = API(csv, useMemory = False, deleteExisting = False)
    connection = api.createDatabase()
    bases = api.getBases()
    for base in bases: print(base)
    connection.close()

if __name__ == "__main__":
    main()