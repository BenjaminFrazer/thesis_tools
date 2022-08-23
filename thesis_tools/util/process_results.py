#!/usr/bin/env ipython
import pandas as pd
from statistics import mean
from nilmtk import DataSet
import re
def combine_and_store_overal_pow_results(results_names,output_name,source_datasets):

    summary_glob = pd.DataFrame()
    for ii, results in enumerate(results_names): # loop through aggreagation levels
        with pd.HDFStore(results) as store:
            summary = store["ResultsSummary"]
        summary["Household"] = [i+1 for i in range(5)]
        summary = summary.set_index("Household")
        summary["Metric"] = "rmse"
        summary["AggLevel"] = ii+1
        summary.set_index("AggLevel",inplace=True,append=True)
        summary_glob =  pd.concat([summary_glob,summary],axis=0)

    if not source_datasets is None:
        summary_glob.reset_index(inplace=True)
        start = pd.Timestamp("2021/04/01 2:00") # should get this from experiment
        end = pd.Timestamp("2021/04/01 12:00")
        for ii,dataset in enumerate(source_datasets):
            ds = DataSet(dataset)
            ds.set_window(start,end)
            this_av_powers=[]
            for i in range(5):
                this_building = i+1
                this_av_powers.append(next(ds.buildings[this_building].elec[1].load())["power"]["active"].mean())
                av_power = mean(this_av_powers)# we will use this to
            summary_glob.loc[summary_glob["AggLevel"]==ii+1,"Average Power"]=av_power
        summary_glob.set_index("AggLevel",inplace=True)
    summary_glob.to_csv(output_name)

def combine_and_store_overal_temp_results(results_names,output_name,inferSamplePeriod=True,fileTag=None):

    summary_glob = pd.DataFrame()
    for ii, results in enumerate(results_names): # loop through aggreagation levels
        with pd.HDFStore(results) as store:
            summary = store["ResultsSummary"]
        summary["Household"] = [i+1 for i in range(5)]
        summary = summary.set_index("Household")
        summary["Metric"] = "rmse"
        summary["AggLevel"] = ii+1
        summary.set_index("AggLevel",inplace=True,append=True)
        summary_glob =  pd.concat([summary_glob,summary],axis=0)

    if inferSamplePeriod:
        if fileTag is None:
            fileTag = "SHDS_Mixed_Temporal"
        summary_glob.reset_index(inplace=True)
        for ii,name in enumerate(results_names):
            # "SHDS_pow_agg_3_temp_agg_60s_results_12-08-22.hdf5"
            # "SHDS_Mixed_Temporal_Agg_360s_results_09-08-22.hdf5"
            sample_period = int(re.search(f"(?<=({fileTag}_[aA]gg_))\d{{2,4}}(?=(s_results_\d{{2}}-\d{{2}}-\d{{2}}[.]hdf5))",name).group(0))
            summary_glob.loc[summary_glob["AggLevel"]==ii+1,"Sample Period (s)"]=sample_period
        summary_glob.set_index("AggLevel",inplace=True)
    summary_glob.to_csv(output_name)
