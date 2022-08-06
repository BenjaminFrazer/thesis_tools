#!/usr/bin/env ipython
import pandas as pd
import numpy as np
import os.path as path
import traceback
import os
import re
from datetime import datetime

def extract_dataset_stats(datasetPath,stats=None, doDebug=True):
    # complete =[];partial=[];empty=[];largest_gap = [];nSamplesInSpan = []
    n_empty =0;n_incomplete = 0;n_complete = 0
    # pcCompletion=[];maxDataStreak=[];nValidSamples=[];pcDataInstreak=[];start=[];end=[];
    if stats is None:
        stats = pd.DataFrame()
    dataset_stats = pd.DataFrame()
    with pd.HDFStore(datasetPath, mode='r') as store:
        houses= [x.replace("/","") for x in store.keys()]
        for HHkey in store.keys():
            ID = HHkey.replace("/","")
            thisHH=store[HHkey].copy()
            thisHH = thisHH.to_frame(name='data')
            thisHH = thisHH[~thisHH.index.duplicated()]
            thisHH.sort_index(ascending=True,inplace=True)
            nsamples=len(thisHH)
            samplePeriod = thisHH.index.to_series().diff().median()
            thisHH = thisHH.resample(samplePeriod).asfreq(fill_value=np.NaN)
            thisHH['isData'] = thisHH['data'].notna()
            if (~thisHH['isData']).all(): # no samples at all
                n_empty+=1
                complete=(False);partial=(False);empty=(True)
                maxDataStreak=0;nValidSamples=0;pcCompletion=0;pcDataInstreak=0
                start=(np.NaN);end=(np.NaN)
                largest_gap=(nsamples)
                nSamplesInSpan=(0)
            elif thisHH['isData'].all(): # all samples are valid
                n_complete+=1
                complete=(True);partial=(False);empty=(False)
                maxDataStreak=(nsamples);nValidSamples=(nsamples);pcCompletion=(100);pcDataInstreak=(100)
                start=(thisHH.index[0]);end=(thisHH.index[-1])
                largest_gap=(0)
                nSamplesInSpan=(nsamples)
            else:
                complete=(False);partial=(True);empty=(False)
                n_incomplete+=1
                thisHH["streak_start"] = (thisHH["isData"].ne(thisHH["isData"].shift()))
                thisHH["streak_no"] = thisHH["streak_start"].cumsum()
                thisHH["streak_count"] = thisHH.groupby("streak_no").cumcount().add(1)
                start=(min(thisHH[thisHH['isData']].index))
                end=(max(thisHH[thisHH['isData']].index))
                thisHH = thisHH.loc[start:end]
                nSamplesInSpan=(len(thisHH))
                # how much uninterupted data we have
                nValidSamples=(thisHH['isData'].sum())
                maxDataStreak=(thisHH.loc[thisHH.loc[thisHH['isData']==True]['streak_count'].idxmax(),'streak_count'])
                if thisHH['isData'].all(): # if the span is fully filled
                    largest_gap=(0)
                else:
                    largest_gap=(thisHH.loc[thisHH.loc[thisHH['isData']==False]['streak_count'].idxmax(),'streak_count'])
                # pcCompletion=(nValidSamples[-1]/nsamples*100)
                # pcDataInstreak=(maxDataStreak[-1]/nsamples*100)

            # if ID == "115D8":
            #     import pdb; pdb.set_trace()
            if doDebug:
                print(f"Processing stats for-> ID:{ID}")# , start:{start}, end:{end}")
            maxGap = largest_gap*samplePeriod
            this_stats = pd.DataFrame({
                'complete':complete,
                'partial':partial,
                'empty':empty,
                'maxStreak':maxDataStreak,
                'maxGap_samples':largest_gap,
                'maxGap':maxGap,
                'start':start,
                'end':end,
                'nValidSamples':nValidSamples,
                'samplePeriod':samplePeriod,
                'nSamplesInSpan':nSamplesInSpan},
                [ID])
            this_stats.index.name = "ID"

            try:
                if not empty:
                    month = start.month
                    year = start.year
                    oneMonthDelta = np.timedelta64(1,"M")
                    months = pd.date_range(start-oneMonthDelta, end, freq='MS').month.tolist()
                    completeness = {f"Comp_M{x+1}":np.nan for x in range(12)}
                    for month in months:
                        monthStart = pd.Timestamp(year=year,month=month,day=1)
                        monthEnd_n=month+1
                        if monthEnd_n== 13:
                            year+=1
                            monthEnd_n=1
                        monthEnd = pd.Timestamp(year=year,month=monthEnd_n,day=1)
                        thisCompleteness = (samplePeriod*(thisHH.loc[monthStart:monthEnd,"isData"].sum()-1))/(monthEnd-monthStart)
                        completeness[f"Comp_M{month}"] = [thisCompleteness]
                    month_completeness = pd.DataFrame.from_dict(completeness)
                    month_completeness.index = [ID]
                    this_stats = pd.concat([this_stats,month_completeness],axis=1,sort=True)
                    # if ID == "CA107":
                    #     import pdb; pdb.set_trace()
                    # import pdb; pdb.set_trace()
            except Exception:
                print(traceback.format_exc())
                import pdb; pdb.set_trace()

            # import pdb; pdb.set_trace()
            dataset_stats = pd.concat([dataset_stats, this_stats],axis=0)
    # import pdb; pdb.set_trace()
    dataset_stats['span']=dataset_stats['end']-dataset_stats['start']
    dataset_stats['span_d']=dataset_stats['span']/np.timedelta64(1, 'D')
    dataset_stats['span_d']=dataset_stats['span_d'].fillna(0)
    dataset_stats['pcSpanCompletion']=dataset_stats['nValidSamples']/dataset_stats['nSamplesInSpan']*100;
    dataset_stats['pcSpanCompletion']=dataset_stats['pcSpanCompletion'].fillna(0)
    dataset_stats['pcSpanInStreak']=dataset_stats['maxStreak']/dataset_stats['nSamplesInSpan']*100;
    dataset_stats['pcSpanInStreak']=dataset_stats['pcSpanInStreak'].fillna(0)
    stats = pd.concat([stats,dataset_stats],axis=1,sort=True)
    stats.index.name = "ID"
    # populate stats dataframe
    return stats


if __name__ == "__main__":

    from synthNilmData.process_raw_household_data import process_raw_household_data
    from synthNilmData.process_raw_heatpump_data import process_raw_heatpump_data
    from config import Paths
    paths = Paths()

    blocklist = ["Car","car","Solar","solar","Heapump","Wind","Turbine","generation"]
    passlist = ["Whole house","Whole House","whole house","Whole Property","whole property","House Supply","house supply"]
    # hhRawData_path = "/home/benjaminf/data/household/2021/Sep21/"
    hhRawData_path = "/home/benjaminf/data/household/2021/"
    hpRawData_path = "/home/benjaminf/data/heat_pump/UK_HeatPump_Data_2013_2015/Cleaned_Energy_Data.mat.mat"
    hpData_path = "proc_hp_data.hdf5"
    hhData_path = "proc_hh_data.hdf5"
    hhStats_path = "hh_data_stats.hdf5"
    hpStats_path = "hp_data_stats.hdf5"

    # try:
    #     os.remove(hhStats_path)
    #     os.remove(hpStats_path)
    #     os.remove(hhData_path)
    #     os.remove(hpData_path)
    # except:
    #     pass

    hh_stats = process_raw_household_data(paths.hhRawDataDir ,paths.hh_proc_data_store, passlist, blocklist,debug=False)
    hh_stats = extract_dataset_stats(paths.hh_proc_data_store,hh_stats)
    hh_stats.to_hdf(paths.hh_proc_stats_store,key="hh_stats",mode="w")

    # process_raw_heatpump_data(paths.hpRawDataMat, paths.hp_proc_data_store)
    hp_stats = extract_dataset_stats(paths.hp_proc_data_store)
    hp_stats.to_hdf(paths.hp_proc_stats_store,key="hp_stats",mode="w")

    print(hh_stats)
