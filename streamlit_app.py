import numpy as np
import pandas as pd
import streamlit as st

import altair as alt

from utils import site_data_abstraction
from utils import data_fetcher
from utils import processing_utils
from utils import graphing
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

""" Hide annoying built-in Streamlit HTML """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.markdown(hide_menu_style, unsafe_allow_html=True)
st.markdown(hide_menu_style, unsafe_allow_html=True)


def get_hours_from_epoch():
    return time.time() // (60 * 60)


@st.cache
def load_data(curr_time):
    data = site_data_abstraction.Data()
    dropdown_options = data_fetcher.get_dropdown_options(data)

    return (data, dropdown_options)


# We need to grab the curr time as a way to smartly cache
curr_time = get_hours_from_epoch()

st.title("nCOVID-19 Visualizer")
data, dropdown_options = load_data(curr_time)

""" Build a placeholder cell """
graph_cell = st.empty()
graph_cell.altair_chart(graphing.build_placeholder_chart())

""" Set up the side bar """
metrics_selector = st.sidebar.multiselect(
    "Metrics", dropdown_options[processing_utils.MEASUREMENT_COL], default=[]
)
countries = st.sidebar.multiselect(
    processing_utils.COUNTRY_COL,
    dropdown_options[processing_utils.ENTITY_COL][processing_utils.COUNTRY_COL],
    default=None,
)
states = st.sidebar.multiselect(
    processing_utils.STATE_COL,
    dropdown_options[processing_utils.ENTITY_COL][processing_utils.STATE_COL],
    default=None,
)
counties = st.sidebar.multiselect(
    "US Counties",
    dropdown_options[processing_utils.ENTITY_COL][processing_utils.COUNTY_COL],
    default=None,
)

""" Upon the 'plot' button being pressed, plot the graph if the parameters are valid """
if st.sidebar.button("Plot"):
    request = data_fetcher.generate_data_fetch_request(
        metrics_selector, countries, states, counties
    )

    if data_fetcher.is_valid_data_fetch_request(request):
        df = data_fetcher.process(
            data=data,
            entities=request["entities"],
            metrics=request["metrics"],
            filter_dict=request["filter_dict"],
        )

        chart = graphing.build_chart(source=df)

        graph_cell.altair_chart(chart)
