#!/usr/bin/env ipython
import pandas as pd
import numpy as np
from pandas.api.types import is_datetime64_any_dtype as is_datetime
from IPython.display import display
import datetime
def print_org_df(df, round_dp=2):
    """Function for printing pretty dataframes in org bable."""
    originalcols = df.columns
    df_Pd_Datetime = df[[column for column in df.columns if is_datetime(df.loc[0,column])]].copy()
    df_Datetime = df[[column for column in df.columns if isinstance(df.loc[0,column],datetime.datetime)]].copy()
    df_Timedelta= df[[column for column in df.columns if isinstance(df.loc[0,column],pd.Timedelta)]].copy()
    df_nonDatetime = df[[column for column in df.columns if not isinstance(df.loc[0,column],datetime.datetime)|is_datetime(df.loc[0,column])|isinstance(df.loc[0,column],pd.Timedelta)]].copy()
    df_nonDatetime = df_nonDatetime.round(round_dp)
    for thiscol in df_Pd_Datetime.columns:
        df_Pd_Datetime.loc[:,thiscol] = df_Pd_Datetime[thiscol].astype(str).str[-30:-14]

    for thiscol in df_Datetime.columns:
        df_Datetime.loc[:,thiscol] = df_Datetime[thiscol].astype(str).str[-30:-14]

    for thiscol in df_Timedelta.columns:
        df_Timedelta.loc[:,thiscol] = df_Timedelta[thiscol].astype(str).str[-30:-13]


    df2print = pd.concat([df_Pd_Datetime,df_nonDatetime,df_Timedelta,df_Datetime],axis=1)
    df2print = df2print.reindex(originalcols, axis=1)

    thisTable2Print =df2print.values.tolist()
    thisTable2Print.insert(0,None)
    thisTable2Print.insert(0,list(df2print.columns))
    display(thisTable2Print)
