# Weather Awareness Sortie Planner (WASP)
An application to help correlate weather data with when you should plan sorties


## Problem Statement
Sorties are often planned without much data/insight as to how weather has historically affected launches.
We propose a simple open platform that will ingest historical weather data, and show data along with a 'heatmap' of ideal timeframes for when to launch sorties to prevent interference from weather.

![alt text](https://github.com/filmo003/flight-weather-heatmap/blob/Dev/D9B57C95-F38A-46D2-A492-1819BC22BC23.jpeg?raw=true)

## Data Sources Used


## How to run
DOCKER
From the root directory of the repository, run
```docker-compose up```

LOCAL
From the ./wasp directory
```python manage.py```
LOCAL TESTS
```python manage.py test```

### Access the GUI
Find the port used in mange.py or in the docker-compose.yml file.
Example if docker compose was used: Go to browser and type ```http://localhost:8000```

## Considerations for Air Gapped Environments and Cloud Deployments
Docker compose will create a container image that you can use in Docker, K8s, or any other container hosting software.
In projects without external dependencies (IE F12 -> network in browser doesn't show external network calls) you can just transfer a container image to air gapped environments and it generally will work.
Currently our maps and graphs provider (Plotly) has external dependencies for map images and html elements. Plotly does have an enterprise solution which can be hosted in its own network, which would help consolidate dependencies for air gapped deployments, but this is a paid solution.
All weather data and aircraft data used is publically available.

## Future Ideas
- Improvements to data storage. Our sqllite database solution worked for our hackathon but can be greatly expanded to be included in a docker deployment (postgres included in docker compose as example)
