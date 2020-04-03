import os
import pandas as pd

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
JHU_CSV_PATH = DIR_PATH + "/data/jhu.csv"


def read_csv(option):
    path = ""
    if option == "JHU":
        path = JHU_CSV_PATH

    return pd.read_csv(path)


def save_csv(option, df):
    if option == "JHU":
        df.to_csv(JHU_CSV_PATH)
