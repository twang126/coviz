import numpy as np
import pandas as pd
import streamlit as st

import altair as alt

from utils import site_data_abstraction
from utils import data_fetcher
from utils import processing_utils
from utils import graphing
from utils import streamlit_ui
from utils import session_state

import time

hide_menu_style = """
        <style>
            #MainMenu {visibility: hidden;}
        </style>"""

hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
"""

open_graph_style = """
    <meta property="og:site_name" content="Coviz-19"/>
    <meta property="og:title" content="nCOVID-19 Data Exploratory Tool"/>
    <meta property="og:description" content="A comprehensive tool to plot and explore any combination of Covid-19 metrics and locations. Backed by all of the world's available, most reliable data."/>
    <meta property="og:url" content="https://coronaviz19.herokuapp.com/">
    <meta property="og:type" content="website" />
    <meta property="og:image" content="https://i.imgur.com/rm14BZI.png"/>
    <link rel="shortcut icon" href="static/favicon/favicon.ico">
    <link rel="icon" href="static/favicon/favicon.ico">
"""

### Hide annoying built-in Streamlit HTML ###
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.markdown(hide_menu_style, unsafe_allow_html=True)
st.markdown(hide_menu_style, unsafe_allow_html=True)

state = session_state.get(prev_request=streamlit_ui.get_default_request())


def get_hours_from_epoch():
    return time.time() // (60 * 60)


@st.cache
def load_data(curr_time):
    data = site_data_abstraction.Data()
    dropdown_options = data_fetcher.get_dropdown_options(data)

    return (data, dropdown_options)


# We need to grab the curr time as a way to smartly cache
curr_time = get_hours_from_epoch()

streamlit_ui.add_header_and_title(st)

if st.checkbox("View Instructions"):
    streamlit_ui.load_instructions(st)

data, dropdown_options = load_data(curr_time)

### Build a placeholder cell ###
st.markdown("""### nCovid-19 Visualizer """)
graph_cell = st.empty()

st.header("Raw Data")
data_cell = st.empty()

### Set up the side bar ###
st.sidebar.markdown("""**QueryBuilder [v1.1](https://github.com/twang126/coviz)**""")
st.sidebar.markdown("""### Select Metric(s): """)
metrics_selector = st.sidebar.multiselect(
    "Type(s) of data to plot",
    dropdown_options[processing_utils.MEASUREMENT_COL],
    default=[
        processing_utils.CONFIRMED_COL,
        processing_utils.DEATHS_COL,
        processing_utils.RECOVERED_COL,
    ],
)

st.sidebar.markdown("""### Select Entities: """)
st.sidebar.text("Note: You can leave options empty.")
countries = st.sidebar.multiselect(
    processing_utils.COUNTRY_COL + "s:",
    dropdown_options[processing_utils.ENTITY_COL][processing_utils.COUNTRY_COL],
    default=["World"],
)

states = st.sidebar.multiselect(
    processing_utils.STATE_COL + "s:",
    dropdown_options[processing_utils.ENTITY_COL][processing_utils.STATE_COL],
)
counties = st.sidebar.multiselect(
    "US Counties:",
    dropdown_options[processing_utils.ENTITY_COL][processing_utils.COUNTY_COL],
)

st.sidebar.markdown("""### Overlay (Optional):""")
overlay_checkbox = st.sidebar.checkbox("Apply overlay")
if overlay_checkbox:
    overlay_metric = st.sidebar.selectbox(
        label="Overlay Metric:",
        options=dropdown_options[processing_utils.MEASUREMENT_COL],
    )

    overlay_threshold = st.sidebar.number_input(label="Overlay Threshold:")
else:
    overlay_metric = None
    overlay_threshold = None

## Add the default plot
default_source_df = data_fetcher.process_request_dict(
    data_obj=data, request=state.prev_request
)
default_chart = graphing.build_chart(source=default_source_df)
graph_cell.altair_chart(default_chart)

plot_button = st.sidebar.button("Plot")
graph_alerts_cell = st.sidebar.empty()

### Upon the 'plot' button being pressed, plot the graph if the parameters are valid ###
if plot_button:
    request = data_fetcher.generate_data_fetch_request(
        metrics_selector,
        countries,
        states,
        counties,
        overlay_checkbox,
        overlay_metric,
        overlay_threshold,
    )

    successfully_updated_chart = False

    if data_fetcher.is_valid_data_fetch_request(request):
        df = data_fetcher.process_request_dict(data_obj=data, request=request)

        if df is not None:
            chart = graphing.build_chart(source=df)

            graph_cell.altair_chart(chart)
            successfully_updated_chart = True
            state.prev_request = request

    if not successfully_updated_chart:
        graph_alerts_cell.markdown(
            "**Graph failed to update**: no data returned for that query."
        )
    else:
        graph_alerts_cell.markdown("")
