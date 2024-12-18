import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import yaml
from datetime import datetime
import calendar


class launch_canx_predictor:
    """class for launch cancellation prediction logic"""

    criteria_dir = "data/launch_criteria.yml"  # Directory for rocket launch criteria
    weather_data_dir = (
        "data/combined_weather_data.csv"  # Directory for hourly weather data
    )

    def __init__(self):
        """Function to initialize class by reading weather and criteria data"""
        # Read the yaml file for launch weather criteria
        with open(self.criteria_dir, "r") as file:
            self.launch_criteria = yaml.safe_load(file)

        # Read in the hourly weather data
        self.weather_data = pd.read_csv(self.weather_data_dir)

    def calculate_cancellations(
        self, platform, site, start_window_date, end_window_date
    ):
        """Function to calculate the cancellation status for each hour within the time window provided

        Args:
            platform (string): name of the rocket platform to calculate cancellations for
            site (string): name of the launch complex site to calculate cancellations for
            start_window_date (string): beginning of the launch window timeframe in format: %m/%d/%Y %H:%M:%S UTC
            end_window_date (string): end of the launch window timeframe in format: %m/%d/%Y %H:%M:%S UTC

        Returns:
            pd.DataFrame: pandas dataframe with cancellation status for each hour in dataset
        """
        # Get the launch criteria for the rocket platform
        criteria = self.launch_criteria[platform]

        # Filter the weather data to the launchpad site
        site_data = self.weather_data.loc[
            self.weather_data["LOCATION"] == site
        ].sort_values(["YEAR", "MONTH", "DAY", "HOUR"])

        # Convert the window start and end times to datetime
        start_date = datetime.strptime(start_window_date, "%m/%d/%Y %H:%M:%S UTC")
        end_date = datetime.strptime(end_window_date, "%m/%d/%Y %H:%M:%S UTC")

        # Ensure the window is not over a year
        if (end_date - start_date).days > 365:
            print("ERROR - DATE RANGE OVER A YEAR")
            return

        # Ensure the end datetime is after the start datetime
        if end_date < start_date:
            print("ERROR - INVALID DATE RANGE")
            return

        # Convert the individual date variables to a datetime variable
        # standardize the years to 2000 for easier filtering. Use 2000 for a leap year
        site_data["DATETIME"] = (
            site_data["MONTH"].astype(str)
            + "/"
            + site_data["DAY"].astype(str)
            + "/"
            + "2000"
            + " "
            + site_data["HOUR"].astype(str)
            + ":00:00"
        )
        site_data["DATETIME"] = pd.to_datetime(site_data["DATETIME"])

        # If the window spans 2 different years
        if end_date.year > start_date.year:
            # replace the start and end date years with 2000 to match datetime
            start_date_std = start_date.replace(year=2000)
            end_date_std = end_date.replace(year=2000)

            # filter the data to the time window
            site_data = site_data.loc[
                (site_data["DATETIME"] >= start_date_std)
                | (site_data["DATETIME"] <= end_date_std)
            ]

            # if the predicted year is not a leap year
            if not calendar.isleap(start_date.year):
                # remove feb 29 from data
                site_data = site_data.loc[
                    ~((site_data["MONTH"] == 2) & (site_data["DAY"] == 29))
                ]

            # convert the year back to start and end date years
            site_data.loc[site_data["DATETIME"] >= start_date_std, "DATETIME"] = (
                site_data.loc[
                    site_data["DATETIME"] >= start_date_std, "DATETIME"
                ].apply(lambda x: x.replace(year=start_date.year))
            )
            site_data.loc[site_data["DATETIME"] <= end_date_std, "DATETIME"] = (
                site_data.loc[site_data["DATETIME"] <= end_date_std, "DATETIME"].apply(
                    lambda x: x.replace(year=end_date.year)
                )
            )
        else:
            # replace the time window date year with 2000
            start_date_std = start_date.replace(year=2000)
            end_date_std = end_date.replace(year=2000)

            # filter the data to the date range of the window
            site_data = site_data.loc[
                (site_data["DATETIME"] >= start_date_std)
                & (site_data["DATETIME"] <= end_date_std)
            ]

            # If it is not a leap year
            if not calendar.isleap(start_date.year):
                # remove Feb 29 from data
                site_data = site_data.loc[
                    ~((site_data["MONTH"] == 2) & (site_data["DAY"] == 29))
                ]

            # change the datetime back to the start and end year
            site_data["DATETIME"] = site_data["DATETIME"].apply(
                lambda x: x.replace(year=start_date.year)
            )

        # reset the index after filtering
        site_data = site_data.reset_index(drop=True)

        # Add platform name to dataset
        site_data["PLATFORM"] = platform

        # Default all cancellation columns to 0 (False)
        site_data["WIND_CANX"] = 0
        site_data["THUNDERSTORM_CANX"] = 0
        site_data["LAUNCHPAD_CANX"] = 0
        site_data["UPPER_AIR_CANX"] = 0
        site_data["TOTAL_CANX"] = 0

        # Cancellation Condition 1: high winds at launchpad
        if criteria["max_launchpad_wind"]["include"]:
            # Find where the wind at launchpad exceeds the limit
            idx = np.where(
                site_data[["WIND_SPD_0K_to_5K", "WINDSPEED"]].max(axis=1)
                > criteria["max_launchpad_wind"]["value"]
            )[0]

            # Where they exceed the limit, set the relevant cancellation flags to 1 (True)
            site_data.loc[idx, "WIND_CANX"] = 1
            site_data.loc[idx, "LAUNCHPAD_CANX"] = 1
            site_data.loc[idx, "TOTAL_CANX"] = 1

        # Cancellation Condition 2: thuderstorm in area
        if criteria["thunderstorm"]["include"]:
            # Find where thunderstorms reported in area
            idx = np.where(site_data["THUNDERSTORM"] == 1)[0]

            # Where they exceed the limit, set the relevant cancellation flags to 1 (True)
            site_data.loc[idx, "THUNDERSTORM_CANX"] = 1
            site_data.loc[idx, "LAUNCHPAD_CANX"] = 1
            site_data.loc[idx, "TOTAL_CANX"] = 1

        # Cancellation Condition 3: thunderstorm in the last X minutes
        if criteria["thunderstorm_cooldown"]["include"]:
            # Find where thunderstorms reported in previous x minutes
            idx = np.where(site_data["THUNDERSTORM"].shift(1) == 1)[0]

            # Where they exceed the limit, set the relevant cancellation flags to 1 (True)
            site_data.loc[idx, "THUNDERSTORM_CANX"] = 1
            site_data.loc[idx, "LAUNCHPAD_CANX"] = 1
            site_data.loc[idx, "TOTAL_CANX"] = 1

        # Cancellation Condition 4: high wind shear at altitude
        if criteria["max_wind_shear"]["include"]:
            # Columns to calculate max shear
            shear_cols = [
                "WIND_SHEAR_10K_to_15K",
                "WIND_SHEAR_15K_to_20K",
                "WIND_SHEAR_20K_to_25K",
                "WIND_SHEAR_25K_to_30K",
                "WIND_SHEAR_30K_to_35K",
                "WIND_SHEAR_35K_to_40K",
            ]

            # Find where the max wind shear exceeds limit
            idx = np.where(
                site_data[shear_cols].max(axis=1) > criteria["max_wind_shear"]["value"]
            )[0]

            # Where they exceed the limit, set the relevant cancellation flags to 1 (True)
            site_data.loc[idx, "WIND_CANX"] = 1
            site_data.loc[idx, "UPPER_AIR_CANX"] = 1
            site_data.loc[idx, "TOTAL_CANX"] = 1

        # Cancellation Condition 5: precipitation at launchpad exceeds allowed limit
        if criteria["max_precipitation"]["include"]:
            # Find where the precipitation amount exceeds limits on launchpad
            idx = np.where(site_data["PRCP"] == 1)[0]

            # Where they exceed the limit, set the relevant cancellation flags to 1 (True)
            site_data.loc[idx, "LAUNCHPAD_CANX"] = 1
            site_data.loc[idx, "TOTAL_CANX"] = 1

        # Cancellation Condition 6: solid cloud layer below allowable temperature
        if criteria["min_cloud_temp"]["include"]:
            # Find where solid cloud layer below temperature limit
            idx = np.where(
                (site_data["CLOUDCOVER"].isin(["BKN", "OVC"]))
                & (site_data["CEILINGTEMP"] <= criteria["min_cloud_temp"]["value"])
            )[0]

            # Where they exceed the limit, set the relevant cancellation flags to 1 (True)
            site_data.loc[idx, "UPPER_AIR_CANX"] = 1
            site_data.loc[idx, "TOTAL_CANX"] = 1

        # Cancellation Condition 7: ceiling below allowed height
        if criteria["min_ceiling"]["include"]:
            # Find where the ceiling is below the limit
            idx = np.where(
                (site_data["CLOUDCOVER"].isin(["BKN", "OVC"]))
                & (site_data["CLOUDCEILING"] <= criteria["min_ceiling"]["value"])
            )[0]

            # Where they exceed the limit, set the relevant cancellation flags to 1 (True)
            site_data.loc[idx, "LAUNCHPAD_CANX"] = 1
            site_data.loc[idx, "TOTAL_CANX"] = 1

        # Cancellation Condition 8: visibility below allowed distance
        if criteria["min_visibility"]["include"]:
            # Find where the visbility is below the limit
            idx = np.where(site_data["VISIBILITY"] <= criteria["min_ceiling"]["value"])[
                0
            ]

            # Where they exceed the limit, set the relevant cancellation flags to 1 (True)
            site_data.loc[idx, "LAUNCHPAD_CANX"] = 1
            site_data.loc[idx, "TOTAL_CANX"] = 1

        # Cancellation Condition 9: temperature at launchpad below limit
        if criteria["min_launchpad_temp"]["include"]:
            # Find where the launchpad temperature is below the limit
            idx = np.where(
                site_data["AIRTEMPERATURE"] < criteria["min_launchpad_temp"]["value"]
            )[0]

            # Where they exceed the limit, set the relevant cancellation flags to 1 (True)
            site_data.loc[idx, "LAUNCHPAD_CANX"] = 1
            site_data.loc[idx, "TOTAL_CANX"] = 1

        # Cancellation Condition 10: temperature at launchpad above limit
        if criteria["max_launchpad_temp"]["include"]:
            # Find where the launchpad temperature is above the limit
            idx = np.where(
                site_data["AIRTEMPERATURE"] > criteria["max_launchpad_temp"]["value"]
            )[0]

            # Where they exceed the limit, set the relevant cancellation flags to 1 (True)
            site_data.loc[idx, "LAUNCHPAD_CANX"] = 1
            site_data.loc[idx, "TOTAL_CANX"] = 1

        # Return the weather data with cancellation flags
        return site_data

    @staticmethod
    def plot_hourly_data(data, platform, site, start_window_date, end_window_date):
        """function to plot the hourly aggregation of cancellation data

        Args:
            data (pd.DataFrame): cancellation data to aggregate
            platform (string): rocket platform used to calculate cancellation rates
            site (string): launchpad site used to calculate cancellation rates
            start_window_date (string): beginning of the launch window timeframe in format: %m/%d/%Y %H:%M:%S UTC
            end_window_date (string): end of the launch window timeframe in format: %m/%d/%Y %H:%M:%S UTC
        """
        # Aggregate the cancellation rates to be hourly
        hourly_data = (
            data.groupby(["MONTH", "DAY", "HOUR"])
            .agg(
                {
                    "WIND_CANX": "mean",
                    "THUNDERSTORM_CANX": "mean",
                    "LAUNCHPAD_CANX": "mean",
                    "UPPER_AIR_CANX": "mean",
                    "TOTAL_CANX": "mean",
                    "DATETIME": "mean",
                }
            )
            .reset_index(drop=False)
        )

        # Sort the values by datetime
        hourly_data = hourly_data.sort_values(["DATETIME"]).reset_index(drop=True)

        # Use the rocket platform and launchpad site to create the chart title
        title = f"{platform.replace('_',' ').capitalize()} Cancellation Rate | {site.capitalize()} ({start_window_date} to {end_window_date})"

        # Create a plot of the hourly cancellation rates over the window
        plt.figure(figsize=(20, 5))
        plt.title(title)
        plt.plot(
            hourly_data["DATETIME"],
            hourly_data["TOTAL_CANX"] * 100,
            color="blue",
            label=platform.replace("_", " ").capitalize(),
        )
        plt.fill_between(
            hourly_data["DATETIME"],
            hourly_data["TOTAL_CANX"] * 100,
            color="blue",
            alpha=0.15,
        )
        plt.ylabel("Cancellation Rate")
        plt.xlim(hourly_data["DATETIME"].min(), hourly_data["DATETIME"].max())
        plt.ylim(0, 105)
        plt.gca().yaxis.set_major_formatter(mticker.PercentFormatter())
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b-%d-%Y %H:00Z"))
        plt.legend(loc="upper right")
        plt.show()

    @staticmethod
    def plot_daily_data(data, platform, site, year):
        """function to plot the daily aggregation of cancellation data

        Args:
            data (pd.DataFrame): cancellation data to aggregate
            platform (string): rocket platform used to calculate cancellation rates
            site (string): launchpad site used to calculate cancellation rates
            year (string): year to display the cancellation rates for
        """
        # Aggregate the cancellation data to be daily
        daily_data = (
            data.groupby(["MONTH", "DAY"])
            .agg(
                {
                    "WIND_CANX": "mean",
                    "THUNDERSTORM_CANX": "mean",
                    "LAUNCHPAD_CANX": "mean",
                    "UPPER_AIR_CANX": "mean",
                    "TOTAL_CANX": "mean",
                }
            )
            .reset_index(drop=False)
        )

        # Create a datetime column to plot the data using individual date parameters
        daily_data["DATETIME"] = (
            daily_data["MONTH"].astype(str)
            + "/"
            + daily_data["DAY"].astype(str)
            + "/"
            + str(year)
        )
        daily_data["DATETIME"] = pd.to_datetime(
            daily_data["DATETIME"], format="%m/%d/%Y"
        )

        # Sort the value by datetime
        daily_data = daily_data.sort_values(["DATETIME"]).reset_index(drop=True)

        # Create a chart title using the rocket platform and launchpad site names
        title = f"{platform.replace('_',' ').capitalize()} Cancellation Rate | {site.capitalize()} ({year})"

        # Create a plot for the daily cancellation rates
        plt.figure(figsize=(20, 5))
        plt.title(title)
        plt.plot(
            daily_data["DATETIME"],
            daily_data["TOTAL_CANX"] * 100,
            color="red",
            label=platform.replace("_", " ").capitalize(),
        )
        plt.fill_between(
            daily_data["DATETIME"],
            daily_data["TOTAL_CANX"] * 100,
            color="red",
            alpha=0.15,
        )
        plt.ylabel("Cancellation Rate")
        plt.xlim(daily_data["DATETIME"].min(), daily_data["DATETIME"].max())
        plt.ylim(0, 105)
        plt.gca().yaxis.set_major_formatter(mticker.PercentFormatter())
        plt.gca().xaxis.set_major_formatter(
            mdates.ConciseDateFormatter(
                plt.gca().xaxis.get_major_locator(),
                formats=["%Y", "%B", "%d", "%H:%M", "%H:%M", "%S.%f"],
            )
        )
        plt.legend(loc="upper right")
        plt.show()

    def predict_launch_window(self, platform, site, start_window_date, end_window_date):
        """function to calculate the cancellation stats for a launch window and plot the results

        Args:
            platform (string): name of the rocket platform to calculate cancellations for
            site (string): name of the launch complex site to calculate cancellations for
            start_window_date (string): beginning of the launch window timeframe in format: %m/%d/%Y %H:%M:%S UTC
            end_window_date (string): end of the launch window timeframe in format: %m/%d/%Y %H:%M:%S UTC
        """
        # Calculate the cancellation flags for the time window
        data = self.calculate_cancellations(
            platform, site, start_window_date, end_window_date
        )

        # Plot the hourly results over the time window
        self.plot_hourly_data(data, platform, site, start_window_date, end_window_date)

    def predict_full_year(self, platform, site, year=str(datetime.now().year)):
        """function to calculate the cancellation stats for the entire year and plot the results

        Args:
            platform (string): name of the rocket platform to calculate cancellations for
            site (string): name of the launch complex site to calculate cancellations for
            year (string, optional): year to calculate the cancellation rates for. Defaults to current year
        """
        # convert the start and end window dates to strings
        start_window_date = f"01/01/{year} 00:00:00 UTC"
        end_window_date = f"12/31/{year} 23:00:00 UTC"

        # Calculate the cancellation rates for the full year
        data = self.calculate_cancellations(
            platform, site, start_window_date, end_window_date
        )

        # Plot the daily cancellation rates
        self.plot_daily_data(data, platform, site, year)


if __name__ == "__main__":
    # initialize the prediction model
    model = launch_canx_predictor()

    # Set the rocket platform to calculate cancellation rates
    platform = "falcon_9"  # ['falcon_9', 'atlas_v', 'ares_i_x', 'artemis_i', 'delta_ii', 'space_shuttle']

    # Set the launchpad site to calculate cancellation rates
    site = "patrick"  # ['patrick', vandenburg']

    # Set the year to calculate cancellation rates
    year = "2024"

    # Get full year cancellation rates for platform and site
    model.predict_full_year(platform, site, year)

    # Set the datetimes for the start and end of the launch window
    start_window_date = "1/29/2024 15:00:00 UTC"  # '%m/%d/%Y %H:%M:%S UTC'
    end_window_date = "1/29/2024 20:00:00 UTC"  # '%m/%d/%Y %H:%M:%S UTC'

    # Get the cancellation rates over the launch window for the platform and site
    model.predict_launch_window(platform, site, start_window_date, end_window_date)
