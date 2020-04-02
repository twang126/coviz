from utils import data_fetcher
from utils import processing_utils

import altair as alt


def add_header_and_title(st):
    st.title("The nCovid Analysis Project")
    st.markdown(
        """Authors: [Tim Wang](https://www.timothyxwang.com) & [Anurag Pradhan](https://www.linkedin.com/in/anuragpradhan2016) | [Github](https://github.com/twang126/coviz)"""
    )

    st.markdown(
        """ 
        Recently, there has been much more data available on the novel coronavirus. However, this data is reported by many different sources without much cohesion. As a result, 
        many existing visualizations can only operate on subsets of this data, not the whole. We have started this project to attempt to consolidate
        all of these different datasets under one common schema and facilitate analytics on all of the world's available, reliable data on the virus.

        The **nCovid Analysis Project** has two main goals:  
        &ensp;&ensp;1. Create a central repository and schema for all of the reliable data reported in the world  
        &ensp;&ensp;2. Allow for queries and visualizations against this data  

        """
    )


def load_instructions(st):
    st.subheader("Usage Guide")

    st.markdown(
        """
    
    There are two main types of filters here. We like to call them Metrics and Entities. A Metric is a measurement you 
    want to query, and an Entity is the location to fetch that Metric for.  

    Here, you can select multiple types and combinations of Metrics and Entities. We have also split up the Entities 
    conveniently into either Countries, Provinces/States, and US Counties.  

    Furthermore, we also provide the ability to *overlay* graphs. **This is optional**. However, it is a powerful feature. 
    An overlay takes in a Metric and a threshold value, and for all of the Entities selected, will overlay the graphs together
    as if they all hit the provided threshold value for the selected Metric at the same date. This helps us adjust graphs by date
    and view them side by side. This feature becomes very interesting because the overlay Metric does **not** have to be incldued in the
    Metrics selected to plot. For the sake of example, let's say we want to look at the curve of Deaths for New York and Italy. If we do not use the
    overlay feature, we can get the plots but they are disjointed because the coronavirus reached New York and Italy at different times. Instead, we may
    want to look at these curves, but **adjust** them as if they both hit 1000 Confirmed cases on the same day. This is a complicated query, but thanks to 
    the overlay feature, it can be done (in English, but easily translatable to our **Query Builder**):  

    > Plot Metrics=**Deaths**  
    > for Entities=**Italy**, **New York**  
    > overlay on Metric=**Confirmed** at Threshold=1000    


    Note that some combinations of Metrics and Entities have no reported data. In this case, you will see a blank graph.  
    Finally, if anything is broken or inconsistent, please do not hesitate to reach out.
    """
    )


def get_default_index(term, lst):
    for i, item in enumerate(lst):
        if item == term:
            return i

    return 0


def get_default_request():
    return data_fetcher.generate_data_fetch_request(
        [
            processing_utils.CONFIRMED_COL,
            processing_utils.RECOVERED_COL,
            processing_utils.DEATHS_COL,
        ],
        ["World"],
        [],
        [],
        False,
        None,
        None,
    )
