## File Names
1. launch_criteria/ - directory containing open source launch vehicle parameters for cancellation
2. 2024_launch_attempts.csv - scraped X account for Cape Canaveral for 2024 launch notifications and cross references them to articles on the result of the launch
3. combined_weather_data.csv - preprocessed weather data for all sites using preprocess_weather_data.ipynb logic
4. launch_canx_prediction.py - logic to do some cancellation math based on rocket parameters and location
5. launch_criteria.yml - YAML files containing each rocket and its associated parameters
6. launch_weather_data.zip - zip file containing raw surface and upper atmosphere data for each launch site
7. preprocess_weather_data.ipynb - quick logic used to process the raw weather data 