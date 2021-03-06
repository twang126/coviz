import os
from io import BytesIO

import pandas as pd
import requests
from kaggle.api.kaggle_api_extended import KaggleApi

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
INTERNATIONAL_CSV_FILENAME = "/data/covid-19-all.csv"
CONFIRMED_CASES_KAGGLE_URL = "gpreda/coronavirus-2019ncov"
US_TESTING_DATA_ROOT_URL = "https://covidtracking.com/api/"
COUNTY_LEVEL_DATA_URL = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv"  # noqa

api = KaggleApi()
api.authenticate()


def download_kaggle_dataset(url):
    api.dataset_download_files(url, DIR_PATH + "/data/", unzip=True, force=True)


def get_international_dataset():
    print("Downloading")
    try:
        download_kaggle_dataset(CONFIRMED_CASES_KAGGLE_URL)
    except Exception as e:
        print(e)

    return pd.read_csv(DIR_PATH + INTERNATIONAL_CSV_FILENAME)


def get_historical_us_testing_data():
    print("Getting historical US data")
    suffix = "us/daily.csv"

    r = requests.get(US_TESTING_DATA_ROOT_URL + suffix)
    csv_string = r.content
    return pd.read_csv(BytesIO(csv_string))


def get_historical_states_testing_data():
    # print("Getting states data")
    # suffix = "states/daily.csv"
    # r = requests.get(US_TESTING_DATA_ROOT_URL + suffix)
    # csv_string = r.content
    return pd.read_json("https://covidtracking.com/api/v1/states/daily.json")


def get_historical_county_level_data():
    return pd.read_csv(COUNTY_LEVEL_DATA_URL)


def get_johns_hopkins_county_level_data():
    print("Getting johns hopkins data")
    deaths = pd.read_csv(
        "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv"
    )
    confirmed = pd.read_csv(
        "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv"
    )

    return deaths, confirmed
