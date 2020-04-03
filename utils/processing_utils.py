import datetime
import numpy as np
import pandas as pd
from functools import cmp_to_key
from itertools import chain
from utils import io_utils
import os.path
from os import path
from collections import OrderedDict

CATEGORY_GRAPHING_COL = "Data"

DATE_COL = "Date"
DEATHS_COL = "Deaths"
CONFIRMED_COL = "Confirmed"
RECOVERED_COL = "Recovered"
COUNTRY_COL = "Country/Region"
STATE_COL = "Province/State"
COUNTY_COL = "County"
NEGATIVE_TEST_COL = "Negative Tests"
TOTAL_TEST_COL = "Total Tests"
HOSPITALIZED_COL = "Hospitalized (cumulative)"
CURRENT_HOSPITALIED_COL = "Hospitalized (current)"
DELTA_COL_SUFFIX = " Daily Increase"
ENTITY_COL = "Entity"
MEASUREMENT_COL = "Value"
DELTA_PERCENT_COL_SUFFIX = " Daily Increase(%)"
CUM_ICU_COL = "ICU (cumulative)"
CUM_VENTILATOR_COL = "Ventilator (cumulative)"
CURR_ICU_COL = "ICU (current)"
CURR_VENTILATOR_COL = "Ventilator (current)"


MEASUREMENT_COLS = [
    DEATHS_COL,
    CONFIRMED_COL,
    RECOVERED_COL,
    NEGATIVE_TEST_COL,
    TOTAL_TEST_COL,
    HOSPITALIZED_COL,
    CUM_ICU_COL,
    CUM_VENTILATOR_COL,
    CURR_ICU_COL,
    CURR_VENTILATOR_COL,
    CURRENT_HOSPITALIED_COL,
]

METRIC_DELTA_COLS = [col + DELTA_COL_SUFFIX for col in MEASUREMENT_COLS]

METRIC_PERCENT_CHANGE_COLS = [
    col + DELTA_PERCENT_COL_SUFFIX for col in MEASUREMENT_COLS
]

METRIC_COLS = sorted(MEASUREMENT_COLS + METRIC_DELTA_COLS + METRIC_PERCENT_CHANGE_COLS)

ENTITY_COLS = [COUNTRY_COL, STATE_COL, COUNTY_COL]

ENTITY_TO_PURE_METRICS = {
    COUNTRY_COL: [DEATHS_COL, CONFIRMED_COL, RECOVERED_COL],
    "International Provinces": [DEATHS_COL, CONFIRMED_COL, RECOVERED_COL],
    "United States": [
        DEATHS_COL,
        CONFIRMED_COL,
        NEGATIVE_TEST_COL,
        TOTAL_TEST_COL,
        HOSPITALIZED_COL,
        CUM_ICU_COL,
        CUM_VENTILATOR_COL,
        CURRENT_HOSPITALIED_COL,
        CURR_ICU_COL,
        CURR_VENTILATOR_COL,
    ],
    "US States": [
        DEATHS_COL,
        CONFIRMED_COL,
        NEGATIVE_TEST_COL,
        TOTAL_TEST_COL,
        HOSPITALIZED_COL,
        CUM_ICU_COL,
        CUM_VENTILATOR_COL,
        CURRENT_HOSPITALIED_COL,
        CURR_ICU_COL,
        CURR_VENTILATOR_COL,
    ],
    "US Counties": [DEATHS_COL, CONFIRMED_COL],
}

ENTITY_TO_METRICS_UNORDERED = {
    k: list(
        chain.from_iterable(
            (i, i + DELTA_COL_SUFFIX, i + DELTA_PERCENT_COL_SUFFIX) for i in v
        )
    )
    for k, v in ENTITY_TO_PURE_METRICS.items()
}

ENTITY_TO_METRICS = OrderedDict()
ENTITY_TO_METRICS[COUNTRY_COL] = ENTITY_TO_METRICS_UNORDERED[COUNTRY_COL]
ENTITY_TO_METRICS["United States"] = ENTITY_TO_METRICS_UNORDERED["United States"]
ENTITY_TO_METRICS["International Provinces"] = ENTITY_TO_METRICS_UNORDERED[
    "International Provinces"
]
ENTITY_TO_METRICS["US States"] = ENTITY_TO_METRICS_UNORDERED["US States"]
ENTITY_TO_METRICS["US Counties"] = ENTITY_TO_METRICS_UNORDERED["US Counties"]


STATE_MAPPING = {
    "AK": "Alaska",
    "AL": "Alabama",
    "AR": "Arkansas",
    "AS": "American Samoa",
    "AZ": "Arizona",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DC": "District of Columbia",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "GU": "Guam",
    "HI": "Hawaii",
    "IA": "Iowa",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "MA": "Massachusetts",
    "MD": "Maryland",
    "ME": "Maine",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MO": "Missouri",
    "MP": "Northern Mariana Islands",
    "MS": "Mississippi",
    "MT": "Montana",
    "NA": "National",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "NE": "Nebraska",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NV": "Nevada",
    "NY": "New York",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "PR": "Puerto Rico",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VA": "Virginia",
    "VI": "Virgin Islands",
    "VT": "Vermont",
    "WA": "Washington",
    "WI": "Wisconsin",
    "WV": "West Virginia",
    "WY": "Wyoming",
}


class CovidDF:
    def __init__(self, df, col_mapping):
        self.df = df

        self.df.rename(columns=col_mapping)
        self.cols = col_mapping.values()

    def aggregate(self, grouping_cols, agg_cols):
        pass


def create_world_df(df, poll=False):
    col_mapping = {
        "Date": DATE_COL,
        "Country/Region": COUNTRY_COL,
        "Province/State": STATE_COL,
        "Confirmed": CONFIRMED_COL,
        "Recovered": RECOVERED_COL,
        "Deaths": DEATHS_COL,
    }

    renamed_df = df.rename(columns=col_mapping)
    renamed_df[COUNTRY_COL] = "World"

    renamed_df = agg_df(
        renamed_df,
        group_cols=[DATE_COL, COUNTRY_COL],
        agg_col=[CONFIRMED_COL, RECOVERED_COL, DEATHS_COL],
    )

    renamed_df = add_rolling_diff(
        renamed_df,
        sort_cols=[DATE_COL, COUNTRY_COL],
        diff_group_cols=[COUNTRY_COL],
        agg_cols=[CONFIRMED_COL, RECOVERED_COL, DEATHS_COL],
    )

    return add_percent_change(
        renamed_df,
        sort_cols=[DATE_COL, COUNTRY_COL],
        diff_group_cols=[COUNTRY_COL],
        agg_cols=[CONFIRMED_COL, RECOVERED_COL, DEATHS_COL],
    )


def post_process_international_df(df, poll=False):
    col_mapping = {
        "Date": DATE_COL,
        "Country/Region": COUNTRY_COL,
        "Province/State": STATE_COL,
        "Confirmed": CONFIRMED_COL,
        "Recovered": RECOVERED_COL,
        "Deaths": DEATHS_COL,
    }

    renamed_df = df.rename(columns=col_mapping)
    renamed_df[COUNTRY_COL] = renamed_df[COUNTRY_COL].apply(
        lambda r: "United States" if r == "US" else r
    )

    renamed_df = agg_df(
        renamed_df,
        group_cols=[DATE_COL, COUNTRY_COL],
        agg_col=[CONFIRMED_COL, RECOVERED_COL, DEATHS_COL],
    )

    renamed_df = add_rolling_diff(
        renamed_df,
        sort_cols=[DATE_COL, COUNTRY_COL],
        diff_group_cols=[COUNTRY_COL],
        agg_cols=[CONFIRMED_COL, RECOVERED_COL, DEATHS_COL],
    )

    return add_percent_change(
        renamed_df,
        sort_cols=[DATE_COL, COUNTRY_COL],
        diff_group_cols=[COUNTRY_COL],
        agg_cols=[CONFIRMED_COL, RECOVERED_COL, DEATHS_COL],
    )


def post_process_international_states_df(df, international_post_processed, poll=False):
    col_mapping = {
        "Date": DATE_COL,
        "Country/Region": COUNTRY_COL,
        "Province/State": STATE_COL,
        "Confirmed": CONFIRMED_COL,
        "Recovered": RECOVERED_COL,
        "Deaths": DEATHS_COL,
    }

    renamed_df = df.rename(columns=col_mapping)
    renamed_df = renamed_df[
        (renamed_df[COUNTRY_COL] != "US")
        & (renamed_df[COUNTRY_COL] != "UK")
        & (renamed_df[COUNTRY_COL] != "None")
    ]
    countries = set(international_post_processed[COUNTRY_COL].unique())
    renamed_df = renamed_df[~renamed_df[STATE_COL].isin(countries)]

    renamed_df = renamed_df.dropna(subset=[STATE_COL])
    renamed_df[STATE_COL] = renamed_df.apply(
        lambda row: row[STATE_COL] + " (" + row[COUNTRY_COL] + ")", axis=1
    )

    renamed_df = agg_df(
        renamed_df,
        group_cols=[DATE_COL, STATE_COL],
        agg_col=[CONFIRMED_COL, RECOVERED_COL, DEATHS_COL],
    )

    renamed_df = add_rolling_diff(
        renamed_df,
        sort_cols=[DATE_COL, STATE_COL],
        diff_group_cols=[STATE_COL],
        agg_cols=[CONFIRMED_COL, RECOVERED_COL, DEATHS_COL],
    )

    return add_percent_change(
        renamed_df,
        sort_cols=[DATE_COL, STATE_COL],
        diff_group_cols=[STATE_COL],
        agg_cols=[CONFIRMED_COL, RECOVERED_COL, DEATHS_COL],
    )


def stable_post_process_us_testing_df(df, poll=False):
    col_mapping = {
        "date": DATE_COL,
        "negative": NEGATIVE_TEST_COL,
        "totalTestResults": TOTAL_TEST_COL,
        "hospitalized": HOSPITALIZED_COL,
        "negativeIncrease": NEGATIVE_TEST_COL + DELTA_COL_SUFFIX,
        "totalTestResultsIncrease": TOTAL_TEST_COL + DELTA_COL_SUFFIX,
        "hospitalizedIncrease": HOSPITALIZED_COL + DELTA_COL_SUFFIX,
    }

    df = df.rename(columns=col_mapping)
    df[COUNTRY_COL] = "United States"
    df[DATE_COL] = df[DATE_COL].astype(str)
    df[DATE_COL] = df[DATE_COL].apply(
        lambda d: datetime.datetime.strptime(d, "%Y%m%d").strftime("%Y-%m-%d")
    )

    df = add_percent_change(
        df,
        sort_cols=[DATE_COL],
        diff_group_cols=[COUNTRY_COL],
        agg_cols=[NEGATIVE_TEST_COL, TOTAL_TEST_COL, HOSPITALIZED_COL,],
    )

    return df


def post_process_us_testing_df(df, poll=False):
    col_mapping = {
        "date": DATE_COL,
        "negative": NEGATIVE_TEST_COL,
        "totalTestResults": TOTAL_TEST_COL,
        "hospitalizedCumulative": HOSPITALIZED_COL,
        "negativeIncrease": NEGATIVE_TEST_COL + DELTA_COL_SUFFIX,
        "totalTestResultsIncrease": TOTAL_TEST_COL + DELTA_COL_SUFFIX,
        "hospitalizedIncrease": HOSPITALIZED_COL + DELTA_COL_SUFFIX,
        "inIcuCurrently": CURR_ICU_COL,
        "inIcuCumulative": CUM_ICU_COL,
        "onVentilatorCurrently": CURR_VENTILATOR_COL,
        "onVentilatorCumulative": CUM_VENTILATOR_COL,
        "hospitalizedCurrently": CURRENT_HOSPITALIED_COL,
    }

    df = df.rename(columns=col_mapping)
    df[COUNTRY_COL] = "United States"
    df[DATE_COL] = df[DATE_COL].astype(str)
    df[DATE_COL] = df[DATE_COL].apply(
        lambda d: datetime.datetime.strptime(d, "%Y%m%d").strftime("%Y-%m-%d")
    )

    df = add_rolling_diff(
        df,
        sort_cols=[DATE_COL],
        diff_group_cols=[COUNTRY_COL],
        agg_cols=[
            CURR_ICU_COL,
            CURR_VENTILATOR_COL,
            CUM_ICU_COL,
            CUM_VENTILATOR_COL,
            CURRENT_HOSPITALIED_COL,
        ],
    )

    df = add_percent_change(
        df,
        sort_cols=[DATE_COL],
        diff_group_cols=[COUNTRY_COL],
        agg_cols=[
            NEGATIVE_TEST_COL,
            TOTAL_TEST_COL,
            HOSPITALIZED_COL,
            CURR_ICU_COL,
            CURRENT_HOSPITALIED_COL,
            CURR_VENTILATOR_COL,
            CUM_ICU_COL,
            CUM_VENTILATOR_COL,
        ],
    )

    return df


def stable_post_process_state_testing_df(df):
    col_mapping = {
        "date": DATE_COL,
        "state": STATE_COL,
        "negative": NEGATIVE_TEST_COL,
        "positive": CONFIRMED_COL,
        "death": DEATHS_COL,
        "hospitalized": HOSPITALIZED_COL,
        "totalTestResults": TOTAL_TEST_COL,
        "positiveIncrease": CONFIRMED_COL + DELTA_COL_SUFFIX,
        "negativeIncrease": NEGATIVE_TEST_COL + DELTA_COL_SUFFIX,
        "totalTestResultsIncrease": TOTAL_TEST_COL + DELTA_COL_SUFFIX,
        "hospitalizedIncrease": HOSPITALIZED_COL + DELTA_COL_SUFFIX,
        "deathIncrease": DEATHS_COL + DELTA_COL_SUFFIX,
    }

    df = df.rename(columns=col_mapping)
    df[DATE_COL] = df[DATE_COL].astype(str)
    df[DATE_COL] = df[DATE_COL].apply(
        lambda d: datetime.datetime.strptime(d, "%Y%m%d").strftime("%Y-%m-%d")
    )

    df[STATE_COL] = df[STATE_COL].apply(
        lambda abbrev: STATE_MAPPING[abbrev] if abbrev in STATE_MAPPING else abbrev
    )

    df[STATE_COL] = df.apply(lambda row: row[STATE_COL] + " (United States)", axis=1)

    return add_percent_change(
        df,
        sort_cols=[DATE_COL, STATE_COL],
        diff_group_cols=[STATE_COL],
        agg_cols=[
            NEGATIVE_TEST_COL,
            CONFIRMED_COL,
            DEATHS_COL,
            TOTAL_TEST_COL,
            HOSPITALIZED_COL,
        ],
    )


def post_process_state_testing_df(df, poll=False):
    col_mapping = {
        "date": DATE_COL,
        "state": STATE_COL,
        "negative": NEGATIVE_TEST_COL,
        "positive": CONFIRMED_COL,
        "death": DEATHS_COL,
        "hospitalizedCumulative": HOSPITALIZED_COL,
        "totalTestResults": TOTAL_TEST_COL,
        "positiveIncrease": CONFIRMED_COL + DELTA_COL_SUFFIX,
        "negativeIncrease": NEGATIVE_TEST_COL + DELTA_COL_SUFFIX,
        "totalTestResultsIncrease": TOTAL_TEST_COL + DELTA_COL_SUFFIX,
        "hospitalizedIncrease": HOSPITALIZED_COL + DELTA_COL_SUFFIX,
        "deathIncrease": DEATHS_COL + DELTA_COL_SUFFIX,
        "inIcuCurrently": CURR_ICU_COL,
        "inIcuCumulative": CUM_ICU_COL,
        "onVentilatorCurrently": CURR_VENTILATOR_COL,
        "onVentilatorCumulative": CUM_VENTILATOR_COL,
        "hospitalizedCurrently": CURRENT_HOSPITALIED_COL,
    }

    df = df.rename(columns=col_mapping)
    df[DATE_COL] = df[DATE_COL].astype(str)
    df[DATE_COL] = df[DATE_COL].apply(
        lambda d: datetime.datetime.strptime(d, "%Y%m%d").strftime("%Y-%m-%d")
    )

    df[STATE_COL] = df[STATE_COL].apply(
        lambda abbrev: STATE_MAPPING[abbrev] if abbrev in STATE_MAPPING else abbrev
    )

    df[STATE_COL] = df.apply(lambda row: row[STATE_COL] + " (United States)", axis=1)

    df = add_rolling_diff(
        df,
        sort_cols=[DATE_COL, STATE_COL],
        diff_group_cols=[STATE_COL],
        agg_cols=[
            CURR_ICU_COL,
            CURR_VENTILATOR_COL,
            CURRENT_HOSPITALIED_COL,
            CUM_ICU_COL,
            CUM_VENTILATOR_COL,
        ],
    )

    return add_percent_change(
        df,
        sort_cols=[DATE_COL, STATE_COL],
        diff_group_cols=[STATE_COL],
        agg_cols=[
            NEGATIVE_TEST_COL,
            CONFIRMED_COL,
            DEATHS_COL,
            TOTAL_TEST_COL,
            HOSPITALIZED_COL,
            CURR_ICU_COL,
            CURR_VENTILATOR_COL,
            CUM_ICU_COL,
            CUM_VENTILATOR_COL,
            CURRENT_HOSPITALIED_COL,
        ],
    )


def post_process_county_df(df, poll=False):
    col_mapping = {
        "date": DATE_COL,
        "county": COUNTY_COL,
        "state": STATE_COL,
        "cases": CONFIRMED_COL,
    }

    renamed_df = df.rename(columns=col_mapping)
    renamed_df[COUNTY_COL] = renamed_df.apply(
        lambda row: row[COUNTY_COL] + " (" + row[STATE_COL] + ")", axis=1
    )
    renamed_df = renamed_df.drop([STATE_COL], inplace=False, axis=1)
    renamed_df = add_rolling_diff(
        renamed_df,
        sort_cols=[DATE_COL, COUNTY_COL],
        diff_group_cols=[COUNTY_COL],
        agg_cols=[CONFIRMED_COL],
    )

    return add_percent_change(
        renamed_df,
        sort_cols=[DATE_COL, COUNTY_COL],
        diff_group_cols=[COUNTY_COL],
        agg_cols=[CONFIRMED_COL],
    )


def post_process_county_df_jhu(deaths, confirmed, overwrite=False):
    if path.exists(io_utils.JHU_CSV_PATH):
        print("Reading JHU CSV from cache")
        return pd.read_csv(io_utils.JHU_CSV_PATH)

    def reformat_date(old):
        old_date = old.split("/")
        yyyy = "20" + old_date[2]
        mm = "0" + old_date[0] if len(old_date[0]) == 1 else old_date[0]
        dd = "0" + old_date[1] if len(old_date[1]) == 1 else old_date[1]
        return yyyy + "-" + mm + "-" + dd

    print("Starting to postprocess JHU")
    death_id_cols = [
        "UID",
        "iso2",
        "iso3",
        "code3",
        "FIPS",
        "Admin2",
        "Province_State",
        "Country_Region",
        "Lat",
        "Long_",
        "Combined_Key",
        "Population",
    ]

    melted_deaths = pd.melt(
        deaths, id_vars=death_id_cols, var_name=DATE_COL, value_name=DEATHS_COL
    )
    melted_deaths["Admin2"] = melted_deaths["Admin2"].fillna("")
    melted_deaths = melted_deaths[(melted_deaths["Admin2"] != "Unassigned")]
    melted_deaths = melted_deaths[~melted_deaths["Admin2"].str.contains("Out of")]
    melted_deaths = melted_deaths.rename(
        columns={"Admin2": "County", "Province_State": "Province/State"}
    )

    # Process confirmed df
    confirmed_id_cols = [
        "UID",
        "iso2",
        "iso3",
        "code3",
        "FIPS",
        "Admin2",
        "Province_State",
        "Country_Region",
        "Lat",
        "Long_",
        "Combined_Key",
    ]

    confirmed_melted = pd.melt(
        confirmed,
        id_vars=confirmed_id_cols,
        var_name=DATE_COL,
        value_name=CONFIRMED_COL,
    )
    confirmed_melted = confirmed_melted.rename(
        columns={"Admin2": "County", "Province_State": "Province/State"}
    )
    confirmed_melted["County"] = confirmed_melted["County"].fillna("")
    confirmed_melted = confirmed_melted[(confirmed_melted["County"] != "Unassigned")]
    confirmed_melted = confirmed_melted[
        ~confirmed_melted["County"].str.contains("Out of")
    ]
    county_confirmed = confirmed_melted[
        ["FIPS", "UID", "County", "Province/State", "Date", "Confirmed"]
    ]
    merged = county_confirmed.merge(melted_deaths, how="outer", on=["UID", DATE_COL])

    merged = merged.rename(
        columns={"Province/State_x": "Province/State", "County_x": "County"}
    )
    merged["County"] = merged.apply(
        lambda row: row["Province/State"]
        if row["County"] == ""
        else row["County"] + " (" + row["Province/State"] + ")",
        axis=1,
    )
    merged = merged[["County", "Deaths", "Confirmed", "Date"]]

    merged["Date"] = merged["Date"].apply(lambda d: reformat_date(d))

    renamed_df = add_rolling_diff(
        merged,
        sort_cols=[DATE_COL, COUNTY_COL],
        diff_group_cols=[COUNTY_COL],
        agg_cols=[CONFIRMED_COL, DEATHS_COL],
    )

    renamed_df = add_percent_change(
        renamed_df,
        sort_cols=[DATE_COL, COUNTY_COL],
        diff_group_cols=[COUNTY_COL],
        agg_cols=[CONFIRMED_COL, DEATHS_COL],
    )

    io_utils.save_csv("JHU", renamed_df)

    return renamed_df


def add_rolling_diff(df, sort_cols, diff_group_cols, agg_cols):
    sorted_df = df.sort_values(by=sort_cols)
    for agg_col_name in agg_cols:
        delta_col_name = agg_col_name + DELTA_COL_SUFFIX
        sorted_df[delta_col_name] = (
            sorted_df.groupby(diff_group_cols)[agg_col_name]
            .diff()
            .fillna(sorted_df[agg_col_name], inplace=False)
        )

    return sorted_df


def agg_df(df, group_cols, agg_col):
    return df.groupby(group_cols)[agg_col].sum().reset_index()


def add_percent_change(df, sort_cols, diff_group_cols, agg_cols):
    sorted_df = df.sort_values(by=sort_cols)
    for agg_col_name in agg_cols:
        delta_col_name = agg_col_name + DELTA_PERCENT_COL_SUFFIX

        if len(diff_group_cols) == 0:
            sorted_df[delta_col_name] = sorted_df[agg_col_name].pct_change()
        else:
            sorted_df[delta_col_name] = sorted_df.groupby(diff_group_cols)[
                agg_col_name
            ].pct_change()

        sorted_df[delta_col_name] = (
            sorted_df[delta_col_name]
            .replace([np.inf, -np.inf], np.nan)
            .fillna(0, inplace=False)
        )
        sorted_df[delta_col_name] = (sorted_df[delta_col_name] * 100).round(1)

    return sorted_df


def get_countries_to_states(international_country_df, post_processed_us_states):
    international_country_df = international_country_df[
        international_country_df[COUNTRY_COL] != "US"
    ]
    countries_to_state = {}

    all_countries = international_country_df[COUNTRY_COL].unique().tolist()

    for country in all_countries:
        these_states = international_country_df[
            international_country_df[COUNTRY_COL] == country
        ][STATE_COL].dropna()
        if len(these_states) == 0:
            continue

        these_states = these_states.unique().tolist()
        countries_to_state[country] = these_states

    countries_to_state["US"] = post_processed_us_states[STATE_COL].unique().tolist()

    return countries_to_state


def get_states_to_counties(counties_df):
    states_to_counties = {}

    all_states = counties_df[STATE_COL].unique().tolist()

    for state in all_states:
        counties = counties_df[counties_df[STATE_COL] == state][COUNTY_COL].dropna()
        if len(counties) == 0:
            continue
        counties = counties.unique().tolist()
        states_to_counties[state] = counties

    return states_to_counties


def get_all_entities(dataframes):
    entities = {}

    all_countries = []
    all_states = []
    all_counties = []

    for df in dataframes:
        countries = []
        states = []
        counties = []

        if COUNTY_COL in df.columns:
            counties = df[COUNTY_COL].unique().tolist()

            all_counties = all_counties + counties
        elif STATE_COL in df.columns:
            has_state_col = True
            states = df[STATE_COL].unique().tolist()
            all_states = all_states + states
        elif COUNTRY_COL in df.columns:
            countries = df[COUNTRY_COL].unique().tolist()

            all_countries = all_countries + countries

    # sort counties by state -> county name
    sorted_counties = list(set(all_counties))
    sorted_counties.sort(key=cmp_to_key(compare))

    # sort states/province by country-> state/province name
    sorted_states = list(set(all_states))
    sorted_states.sort(key=cmp_to_key(compare))

    entities[COUNTRY_COL] = sorted(set(all_countries))
    entities[STATE_COL] = sorted_states
    entities[COUNTY_COL] = sorted_counties

    return entities


def compare(entity1, entity2):
    if entity1.find("(") < entity1.find(")") and entity2.find("(") < entity2.find(")"):
        if entity1[entity1.find("(") + 1 : entity1.find(")")] == (
            entity2[entity2.find("(") + 1 : entity2.find(")")]
        ):
            return -1 if entity1 < entity2 else 1
        else:
            return (
                -1
                if entity1[entity1.find("(") + 1 : entity1.find(")")]
                < (entity2[entity2.find("(") + 1 : entity2.find(")")])
                else 1
            )
    else:
        return -1 if entity1 < entity2 else 1


def create_hierarchy(all_entities):
    hierarchy = {
        COUNTRY_COL: all_entities[COUNTRY_COL],
        STATE_COL: all_entities[STATE_COL],
        COUNTY_COL: all_entities[COUNTY_COL],
    }

    # all_states = all_entities[STATE_COL]

    # country_to_state['Unlinked'] = []
    # for state in all_states:
    #     contained = False

    #     for mapped_state in country_to_state.values():
    #         if state in mapped_state:
    #             contained = True
    #             break

    #     if not contained:
    #         country_to_state['Unlinked'].append(state)

    # state_to_county['Unlinked'] = []
    # for county in all_entities[COUNTY_COL]:
    #     contained = False

    #     for mapped_county in state_to_county.values():
    #         if county in mapped_county:
    #             contained = True
    #             break

    #     if not contained:
    #         state_to_county['Unlinked'].append(county)

    # hierarchy[STATE_COL] = list(country_to_state.values())
    # hierarchy[COUNTY_COL] = list(state_to_county.values())

    return hierarchy
