def add_header_and_title(st):
    st.title("The nCovid Analysis Project")
    st.markdown(
        """Authors: [Tim Wang]() & [Anurag Pradhan]() | [Github](https://github.com/twang126/coviz)"""
    )

    st.markdown(
        """ 
        As the novel coronavirus continues to spread throughout the globe, more and more data is becoming more
        available to us for a handful of different metrics, each reported by different countries and regions in the 
        world. However, this data comes from many different sources- the WHO, individual health departments, etc. and 
        indeed, many visualizations can only operate on subsets of this data.  

        The nCovid Analysis Project has two main goals:  
          1.  Create a central repository and schema for all of the reliable data reported in the world  
          2.  Allow for queries and visualizations against this data
        """
    )
