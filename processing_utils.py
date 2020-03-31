import datetime
import numpy as np

DATE_COL = "Date"
DEATHS_COL = "Deaths"
CONFIRMED_COL = "Confirmed"
RECOVERED_COL = "Recovered"
COUNTRY_COL = "Country/Region"
STATE_COL = "Province/State"
COUNTY_COL = "County"
NEGATIVE_TEST_COL = "Negative Tests"
TOTAL_TEST_COL = "Total Tests"
HOSPITALIZED_COL = "Hospitalized"
DELTA_COL_SUFFIX = " Daily Increase"
ENTITY_COL = "Entity"
MEASUREMENT_COL = "Metric"
DELTA_PERCENT_COL_SUFFIX = " Daily Increase(%)"


MEASUREMENT_COLS = [
    DEATHS_COL,
    CONFIRMED_COL,
    RECOVERED_COL,
    NEGATIVE_TEST_COL,
    TOTAL_TEST_COL,
    HOSPITALIZED_COL,
]

METRIC_DELTA_COLS = [col + DELTA_COL_SUFFIX for col in MEASUREMENT_COLS]

METRIC_PERCENT_CHANGE_COLS = [
    col + DELTA_PERCENT_COL_SUFFIX for col in MEASUREMENT_COLS
]

METRIC_COLS = MEASUREMENT_COLS + METRIC_DELTA_COLS + METRIC_PERCENT_CHANGE_COLS

ENTITY_COLS = [COUNTRY_COL, STATE_COL, COUNTY_COL]

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


def post_process_international_df(df):
    col_mapping = {
        "Date": DATE_COL,
        "Country/Region": COUNTRY_COL,
        "Province/State": STATE_COL,
        "Confirmed": CONFIRMED_COL,
        "Recovered": RECOVERED_COL,
        "Deaths": DEATHS_COL,
    }

    renamed_df = df.rename(columns=col_mapping)
    renamed_df = renamed_df[renamed_df[COUNTRY_COL] != "US"]

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


def post_process_international_states_df(df):
    col_mapping = {
        "Date": DATE_COL,
        "Country/Region": COUNTRY_COL,
        "Province/State": STATE_COL,
        "Confirmed": CONFIRMED_COL,
        "Recovered": RECOVERED_COL,
        "Deaths": DEATHS_COL,
    }

    renamed_df = df.rename(columns=col_mapping)
    renamed_df = renamed_df[renamed_df[COUNTRY_COL] != "US"]
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


def post_process_us_testing_df(df):
    col_mapping = {
        "date": DATE_COL,
        "positive": CONFIRMED_COL,
        "negative": NEGATIVE_TEST_COL,
        "totalTestResults": TOTAL_TEST_COL,
        "hospitalized": HOSPITALIZED_COL,
        "death": DEATHS_COL,
        "positiveIncrease": CONFIRMED_COL + DELTA_COL_SUFFIX,
        "negativeIncrease": NEGATIVE_TEST_COL + DELTA_COL_SUFFIX,
        "totalTestResultsIncrease": TOTAL_TEST_COL + DELTA_COL_SUFFIX,
        "hospitalizedIncrease": HOSPITALIZED_COL + DELTA_COL_SUFFIX,
        "deathIncrease": DEATHS_COL + DELTA_COL_SUFFIX,
    }

    df = df.rename(columns=col_mapping)
    df[COUNTRY_COL] = "US"
    df[DATE_COL] = df[DATE_COL].astype(str)
    df[DATE_COL] = df[DATE_COL].apply(
        lambda d: datetime.datetime.strptime(d, "%Y%m%d").strftime("%Y-%m-%d")
    )

    return add_percent_change(
        df,
        sort_cols=[DATE_COL],
        diff_group_cols=[COUNTRY_COL],
        agg_cols=[
            NEGATIVE_TEST_COL,
            CONFIRMED_COL,
            DEATHS_COL,
            TOTAL_TEST_COL,
            HOSPITALIZED_COL,
        ],
    )


def post_process_state_testing_df(df):
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


def post_process_county_df(df):
    col_mapping = {
        "date": DATE_COL,
        "county": COUNTY_COL,
        "state": STATE_COL,
        "cases": CONFIRMED_COL,
        "deaths": DEATHS_COL,
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
        agg_cols=[CONFIRMED_COL, DEATHS_COL],
    )

    return add_percent_change(
        renamed_df,
        sort_cols=[DATE_COL, COUNTY_COL],
        diff_group_cols=[COUNTY_COL],
        agg_cols=[CONFIRMED_COL, DEATHS_COL],
    )


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

    entities[COUNTRY_COL] = list(set(all_countries))
    entities[STATE_COL] = list(set(all_states))
    entities[COUNTY_COL] = list(set(all_counties))

    return entities


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
