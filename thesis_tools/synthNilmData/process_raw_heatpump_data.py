#!/usr/bin/env ipython
import scipy.io
import pandas as pd
import numpy as np
from datetime import datetime
import pandas as pd

# def process_raw_household_data(dataDirPath,dataOut,siteMeterPassList=None,siteSuitibilityColDescBlockList=None, debug=True, TZ='Europe/London'):
def process_raw_heatpump_data(dataDirPath, dataOut, debug=True, TZ = 'Europe/London'):
    data = scipy.io.loadmat(dataDirPath)
    cleaned_data = data['ArrayEnergyClean']
    headings = cleaned_data[0,:]
    body = cleaned_data[1:]

    # convert to float so we can set missing as NaN
    cleaned_data_body =body.astype(float)
    # set missing (-1) values to NaN
    cleaned_data_body[cleaned_data_body==-1]=np.NaN
    nsamples = len(cleaned_data_body[:,0])
    # start date is given as first of jan 2012
    startDate = datetime(2012,1,1)
    # define the index as a datetime - heatpump data is given in 2min increments
    dateStamps = pd.date_range(startDate,periods=nsamples,freq="2T",tz=TZ)
    # create dataframe
    df = pd.DataFrame(cleaned_data_body,columns=headings,index=dateStamps)
    df= df.multiply(30) # heatpump data given in wh/2min so factor of 30 required to get it in watts

    with pd.HDFStore(dataOut, mode='w') as store:
        for thisCol in df.columns:
            thisCol_key = f"HP{thisCol}"
            store.put(thisCol_key,df[thisCol].rename(thisCol_key))
    return
