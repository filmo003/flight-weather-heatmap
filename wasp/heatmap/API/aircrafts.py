class Aircrafts:
    def __init__(self):
        self.__aircrafts = {
            "global-Hawk": {
                "takeoffTime": 8,
                "takeoffWindow": 4,
                "landingTime": 17,
                "landingWindow": 4,
                "altitude": 55000,
                "crosswind": 15,
                "maxwind": 30,
                "windGust": 10,
                "ceiling": 1000,
                "visibility": 0,
                "icing": "med",
                "highTemp": 140,
                "lowTemp": -40,
                "RCR": 7,
                "thunderstorm": 1,
                "freezingRain": 1,
                "hail": 1,
                "fog": 0,
            },
            "f-35": {
                "takeoffTime": 7,
                "takeoffWindow": 4,
                "landingTime": 16,
                "landingWindow": 4,
                "altitude": 40000,
                "crosswind": 20,
                "maxwind": 35,
                "windGust": 15,
                "ceiling": 1500,
                "visibility": 5,
                "icing": "med",
                "highTemp": 140,
                "lowTemp": -40,
                "RCR": 7,
                "thunderstorm": 1,
                "freezingRain": 1,
                "hail": 1,
                "fog": 1,
            },
        }

    def getData(self, aircraft):
        if aircraft in self.__aircrafts:
            return self.__aircrafts[aircraft]
        else:
            raise Exception("Aircrafts dictionary has no key: " + aircraft)
