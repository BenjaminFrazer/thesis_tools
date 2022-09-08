#!/usr/bin/env ipython
"""Script to run sweeps with the experimentation API"""
##### imports #####################################################
import datetime
from contextlib import redirect_stdout
from thesis_tools.util import paths
from thesis_tools.util import data
from nilmtk.api import API
from nilmtk.disaggregate import CO, Mean, FHMMExact
from nilmtk_contrib.disaggregate import DAE, Seq2Seq, Seq2Point
import pandas as pd

##### Experiment Configureation ####################################
power_agg_levels_2_test = [1,2,3] #,3,4,5]
samplePeriods2Test= [120*60, 180*60,240*60,300*60] #[(x+1)*60 for x in range(15)]
# samplePeriods2Test= [300*60] #[(x+1)*60 for x in range(15)]
dateString = (datetime.datetime.now()).strftime("%d-%m-%y")
sweep_summary_file = paths.results+f"/SHDS_sweep_summary_{dateString}.csv"
results_fstring= "/SHDS_results_{dateString}_PAgg{pAgg}_Ts{Ts}.hdf5"

##### Figure out file paths ########################################
hdf_filename =f"{paths.synth_data_path}/SHDS_05-08-22.hdf5"
datasets = paths.synth_data_dict

def construct_experiment_dic(dataset, sample_period, results_name):
    """Creates a single testcase experiment definition dictionary."""
    train_timeframe = {'start_time': '2021-01-01',
                    'end_time':   '2021-04-01'}
    test_timeframe =  {'start_time': '2021-04-01',
                    'end_time':   '2021-05-01'}
    buildings_test = {x+1 : test_timeframe for x in range(5)}
    buildings_train = {x+1 : train_timeframe for x in range(5)}
    experiment = {
    'power': {'mains': ['active'],'appliance': ['active']},
    'do_store_results': True,
    'results_store_name': results_name,
    'sample_rate': sample_period,
    'appliances': ['heat pump'],
    'methods': {"CO":CO({}),
                "FMHH":FHMMExact({'num_of_states':2}),
                'Mean':Mean({}),
                 "DAE":DAE({}),
                 'Seq2Point':Seq2Point({}),
                 'Seq2Seq':Seq2Seq({})
                },
    'train': {
        'datasets': {
                'shds': {
                    'path': dataset,
                    'buildings': buildings_train}}},
    'test': {
        'datasets': {
                'shds': {
                    'path': dataset,
                    'buildings': buildings_test}},
        'metrics':['rmse']}}
    return experiment

def append_new_result(summary_df,result_name,powAggLevel,samplePeriod,itteration):
    """Adds a new result onto the sweep summary."""
    with pd.HDFStore(result_name) as store:
        this_summary = store["ResultsSummary"]
    this_summary["Household"] = [i+1 for i in range(5)]
    this_summary["Metric"] = "rmse"
    this_summary["Itteration"] = itteration
    this_summary["PowAggLevel"] = powAggLevel
    this_summary["SamplePeriod(s)"] = samplePeriod
    this_summary["ResultsFileName"] = result_name
    return pd.concat([summary_df,this_summary],axis=0,sort=False)

summary_glob = pd.DataFrame()
i = 0
for pow_agg_level in power_agg_levels_2_test:
    dataset = datasets[pow_agg_level]
    for sample_period in samplePeriods2Test:
        i+=1
        this_result_name = paths.results+results_fstring.format(pAgg = pow_agg_level,Ts=sample_period,dateString=dateString)
        experiment = construct_experiment_dic(dataset=dataset,sample_period=sample_period,results_name=this_result_name)
        # run the experiment
        API(experiment)
        # add the experimental results to the global summary
        summary_glob = append_new_result(summary_glob,this_result_name,pow_agg_level,sample_period,i)

summary_glob.set_index("Itteration",drop=True, inplace=True)
summary_glob.to_csv(sweep_summary_file)
