#!/usr/bin/env ipython
import numpy as np
import matplotlib.pyplot as plt

def plot_data_availability(df):
    scaling=[x for x in  range(1,len(df.columns)+1)]
    isData=df.apply(np.isnan)#.replace({True:np.NaN,False:1})
    fig = plt.figure()
    ax = fig.add_subplot()
    for i, col in enumerate(isData.columns):
        thisData=isData[[col]]
        thisData = thisData[thisData[col].ne(thisData[col].shift(1))|thisData[col].ne(thisData[col].shift(-1))]
        thisData = thisData.replace({True:np.NaN,False:1})
        thisData = thisData*scaling[i]
        thisax =thisData.plot(ax=ax)
        thisax.set_yticks([])
