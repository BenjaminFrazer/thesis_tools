#!/usr/bin/env ipython
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from thesis_tools.config import Data
data = Data()

def plot_data_availability(stats:pd.DataFrame,store:pd.HDFStore):
    stats.reset_index(inplace=True)
    with store:
        df = pd.concat(map(store.get, stats["ID"]), axis=1)
    df.columns = list(stats["ID"])
    scaling=[x for x in  range(1,len(df.columns)+1)]
    isData=df.apply(np.isnan)#.replace({True:np.NaN,False:1})
    fig = plt.figure()
    ax = fig.add_subplot()
    nplots = len(stats)
    span= df.index[-1]-df.index[0]
    timestamp_label = df.index[-1]+(span)*0.02
    for i, col in enumerate(isData.columns):
        thisData=isData[[col]]
        thisData = thisData[thisData[col].ne(thisData[col].shift(1))|thisData[col].ne(thisData[col].shift(-1))]
        thisData = thisData.replace({True:np.NaN,False:1})
        thisData = thisData*scaling[i]
        thisData.plot(ax=ax,legend=False)
        plt.text(timestamp_label,(i+1),col,bbox=dict(facecolor='w', edgecolor='black',alpha=0.8))
    ax.set_yticks([])
    ax.set_xlim([df.index[0]-span*0.01,df.index[-1]+span*0.01])
