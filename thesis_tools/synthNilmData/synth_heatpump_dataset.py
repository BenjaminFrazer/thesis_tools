#!/usr/bin/env ipython
import pdb
from nilmtk import appliance, timeframe
import pandas as pd
import numpy as np
import yaml
import os.path as path
import os
import re
from datetime import datetime
from nilmtk.datastore import Key
from nilmtk.datastore import HDFDataStore
from .calc_optimal_allignment_shift_years import calc_optimal_allignment_shift_years

def synth_heatpump_dataset(hp_store, hp_stats, hh_store, hh_stats, meter_devices_file, output_file, targetHouseholds=5):
    # figure out the higest samplerate and use that to synthesise the site meter dataset
    hp_appliance_instance = 1 # how many heatpumps do we have
    sm_meter_instance = 1 # the instance of the sitemeter (indexes this data in the store)
    hp_meter_instance = 2 # index of the heatpump meter (indexes this data in the store)
    hp_appliance_meters = [2] # which meters are directly upstream of the heatpump appliance (given as list)
    ends = [] # track the end times of the synthesised datasets
    starts = []
    for i in range(targetHouseholds): # loop through the top n of the selected household and heatpump datasets and combine
        buildingInst = i+1 # nilm convention to start naming buildings from 1
        key_sm= Key(building=buildingInst, meter=sm_meter_instance) # this uniquely identifies a meter dataset in the store
        key_hp = Key(building=buildingInst, meter=hp_meter_instance) # this uniquely identifies a meter dataset in the store
        this_hh_id = hh_stats.loc[i,'ID'] # the ID of the household dataset
        this_hh_start = hh_stats.loc[i,'start'] # the start of this household dataset
        this_hp_id = hp_stats.loc[i,'ID'] # the ID of the heatpump dataset
        this_hp_start = hp_stats.loc[i,'start'] # the start of the heatpump dataset

        samplePeriod_hh=hh_stats.loc[i,'samplePeriod']
        samplePeriod_hp=hp_stats.loc[i,'samplePeriod']
        selected_samplePeriod = min(samplePeriod_hh, samplePeriod_hp)

        building_key = f'building{buildingInst}'  # e.g. 'building1' # this points to the building level of the store
        this_timeframe =[] # timeframe of this perticular household's worth of data
        hhOriginalName = ""
        hpOriginalName = ""
        original_name= {'hp':hpOriginalName, 'hh':hhOriginalName} # optional field that allows us to track down the origin of the data
        building_key = f'building{buildingInst}'  # e.g. 'building1'

        # build and store the metadata for this household
        hp_appliance_metadata = gen_hp_appliance_metadata(hp_appliance_instance,hp_appliance_meters)
        meter_metadata_hp = gen_hp_meter_metadata(buildingInst,key_hp)
        meter_metadata_sm = gen_hh_meter_metadata(buildingInst,key_sm)

        meter_metadata = {hp_meter_instance:meter_metadata_hp,sm_meter_instance:meter_metadata_sm}
        building_metadata = gen_building_metadata(buildingInst,[hp_appliance_metadata],meter_metadata,this_timeframe,original_name)
        store_building_metadata(building_metadata, building_key,output_file)


        # import pdb; pdb.set_trace()
        this_hp_data=hp_store[this_hp_id].copy()
        this_hh_data=hh_store[this_hh_id].copy()

        this_hp_end = hp_stats.loc[i,'end']
        this_hh_end = hh_stats.loc[i,'end']

        timeshift_hh_years = calc_optimal_allignment_shift_years([1,3],[this_hp_start, this_hp_end],[this_hh_start,this_hh_end])
        timeshift_hh = np.timedelta64(timeshift_hh_years,"Y")

        #synthesise dataset
        # selected_span=min(hh_span,hp_span) # select smallest span as the range of data to write
        synth_dataset_start = max(this_hp_start,this_hh_start+timeshift_hh)
        synth_dataset_end = min(this_hp_end,this_hh_end+timeshift_hh)
        ends.append(synth_dataset_end)
        starts.append(synth_dataset_start)

        this_hh_data.index = this_hh_data.index + timeshift_hh

        this_hp_data = this_hp_data[synth_dataset_start:synth_dataset_end]
        this_hh_data = this_hh_data[synth_dataset_start:synth_dataset_end]

        this_hp_2_add = this_hp_data.resample(selected_samplePeriod).pad()
        this_hh_2_add = this_hh_data.resample(selected_samplePeriod).pad()
        this_sm_data = this_hp_2_add+this_hh_2_add # sitemeter is the summation of heatpump and household data


        #store synthesises dataset
        multicol= pd.MultiIndex.from_tuples([('power', 'active')]) # format required by nilmtk
        this_sm_data = this_sm_data.to_frame()
        this_hp_data = this_hp_data.to_frame()
        this_sm_data.columns = multicol
        this_hp_data.columns = multicol
        store_data(output_file,this_sm_data,key_sm)
        store_data(output_file,this_hp_data,key_hp)

    # build and store the metadata for the dataset
    metadata = gen_dataset_metadata(meter_devices_file,min(starts),max(ends))
    synth_dataset_source_metadata = pd.concat([hh_stats.loc[0:targetHouseholds-1,"ID"].rename("HH_ID"), hp_stats.loc[0:targetHouseholds-1,"ID"].rename("HP_ID")],axis=1)
    metadata["synthetic_data_source"] = synth_dataset_source_metadata
    store_dataset_metadata(metadata, output_file)
    print("Done writing HDF5!")
    return

def synth_heatpump_agregate_dataset(hp_store, hp_stats, hh_store, hh_stats, meter_devices_file, output_file, targetHouseholds=5,aggregation_level=1):
    # this method will combine each heatpump with the same agregate household data to simulate a feeder level mesurement with increaseing agregation level
    # figure out the higest samplerate and use that to synthesise the site meter dataset
    hp_appliance_instance = 1 # how many heatpumps do we have
    sm_meter_instance = 1 # the instance of the sitemeter (indexes this data in the store)
    hp_meter_instance = 2 # index of the heatpump meter (indexes this data in the store)
    hp_appliance_meters = [2] # which meters are directly upstream of the heatpump appliance (given as list)
    MOI = [1,4]
    ends = [] # track the end times of the synthesised datasets
    starts = []


    agg_hh_start = hh_stats.loc[0,"start"]
    agg_hh_end= hh_stats.loc[0,"end"]
    hh_agg_data = pd.Series()
    for i in range(aggregation_level): # here we will allign and sum up all of the household data
        this_hh_id = hh_stats.loc[i,'ID'] # the ID of the household dataset
        this_hh_start = hh_stats.loc[i,'start'] # the start of this household dataset
        this_hh_end = hh_stats.loc[i,'end']
        timeshift_this_hh_years= calc_optimal_allignment_shift_years(MOI,[agg_hh_start, agg_hh_end],[this_hh_start,this_hh_end])
        timeshift_this_hh = np.timedelta64(timeshift_this_hh_years,"Y")
        # this acts to narrow down the aggregate span to the span in which all datasets have data bc we will get nan's everywher else
        agg_hh_start = max(this_hh_start+timeshift_this_hh,agg_hh_start)
        agg_hh_end= min(this_hh_end+timeshift_this_hh,agg_hh_end)
        this_hh_data=hh_store[this_hh_id].copy()
        this_hh_data.index = this_hh_data.index + timeshift_this_hh
        this_hh_data_2_add = this_hh_data[agg_hh_start:agg_hh_end]
        hh_agg_data = hh_agg_data.add(this_hh_data_2_add,fill_value=0)

    for i in range(targetHouseholds): # loop through the top n of the selected household and heatpump datasets and combine
        buildingInst = i+1 # nilm convention to start naming buildings from 1
        key_sm= Key(building=buildingInst, meter=sm_meter_instance) # this uniquely identifies a meter dataset in the store
        key_hp = Key(building=buildingInst, meter=hp_meter_instance) # this uniquely identifies a meter dataset in the store
        this_hp_id = hp_stats.loc[i,'ID'] # the ID of the heatpump dataset
        this_hp_start = hp_stats.loc[i,'start'] # the start of the heatpump dataset
        this_hp_end = hp_stats.loc[i,'end']

        samplePeriod_hh=hh_stats.loc[i,'samplePeriod']
        samplePeriod_hp=hp_stats.loc[i,'samplePeriod']
        selected_samplePeriod = min(samplePeriod_hh, samplePeriod_hp)

        building_key = f'building{buildingInst}'  # e.g. 'building1' # this points to the building level of the store
        this_timeframe =[] # timeframe of this perticular household's worth of data
        hhOriginalName = ""
        hpOriginalName = ""
        original_name= {'hp':hpOriginalName, 'hh':hhOriginalName} # optional field that allows us to track down the origin of the data
        building_key = f'building{buildingInst}'  # e.g. 'building1'

        # build and store the metadata for this household
        hp_appliance_metadata = gen_hp_appliance_metadata(hp_appliance_instance,hp_appliance_meters)
        meter_metadata_hp = gen_hp_meter_metadata(buildingInst,key_hp)
        meter_metadata_sm = gen_hh_meter_metadata(buildingInst,key_sm)

        meter_metadata = {hp_meter_instance:meter_metadata_hp,sm_meter_instance:meter_metadata_sm}
        building_metadata = gen_building_metadata(buildingInst,[hp_appliance_metadata],meter_metadata,this_timeframe,original_name)
        store_building_metadata(building_metadata, building_key,output_file)


        this_hp_data=hp_store[this_hp_id].copy()

        # if this_hp_id== "HP5317":
        #     import pdb; pdb.set_trace()
        timeshift_hp_years = calc_optimal_allignment_shift_years(MOI,[agg_hh_start,agg_hh_end],[this_hp_start, this_hp_end])
        timeshift_hp = np.timedelta64(timeshift_hp_years,"Y")
        this_hp_data.index = this_hp_data.index + timeshift_hp
        this_hp_start = this_hp_start+timeshift_hp
        this_hp_end= this_hp_end+timeshift_hp

        #synthesise dataset
        synth_dataset_start = max(this_hp_start,agg_hh_start)
        synth_dataset_end = min(this_hp_end,agg_hh_end)
        ends.append(synth_dataset_end)
        starts.append(synth_dataset_start)

        this_hh_agg_data_2_add = hh_agg_data[synth_dataset_start:synth_dataset_end]

        this_hp_data = this_hp_data[synth_dataset_start:synth_dataset_end]

        this_hp_2_add = this_hp_data.resample(selected_samplePeriod).pad()
        this_hh_agg_data_2_add = this_hh_agg_data_2_add.resample(selected_samplePeriod).pad()
        this_sm_data = this_hp_2_add+this_hh_agg_data_2_add # sitemeter is the summation of heatpump and household data

        #store synthesises dataset
        multicol= pd.MultiIndex.from_tuples([('power', 'active')]) # format required by nilmtk
        this_sm_data = this_sm_data.to_frame()
        this_hp_data = this_hp_data.to_frame()
        this_sm_data.columns = multicol
        this_hp_data.columns = multicol
        store_data(output_file,this_sm_data,key_sm)
        store_data(output_file,this_hp_data,key_hp)

    # build and store the metadata for the dataset
    metadata = gen_dataset_metadata(meter_devices_file,min(starts),max(ends))
    hh_agg_stats = hh_stats.loc[0:aggregation_level-1,["ID"]]
    hh_agg_stats = hh_agg_stats
    hh_agg_stats = hh_agg_stats.T
    hh_agg_stats = hh_agg_stats.append([hh_agg_stats]*4,ignore_index=True)
    hh_agg_stats.columns = [f"HH_{x}" for x in hh_agg_stats.columns]
    # import pdb; pdb.set_trace()
    synth_dataset_source_metadata = pd.concat([hp_stats.loc[0:targetHouseholds-1,"ID"].rename("HP_ID"),hh_agg_stats],axis=1)
    metadata["synthetic_data_source"] = synth_dataset_source_metadata
    store_dataset_metadata(metadata, output_file)
    print("Done writing HDF5!")
    return

def store_data(hdf_filename,this_data,key):
    store = HDFDataStore(hdf_filename, 'a')
    store.open(mode='a')
    try:
        store.put(str(key), this_data)
    finally:
        store.close()
        del store
    return

def store_building_metadata(building_metadata, building_key,hdf_filename ):
    with pd.HDFStore(hdf_filename, 'a') as store_pd:
        try:
            group = store_pd._handle.create_group('/', building_key)
        except:
            group = store_pd._handle.get_node('/' + building_key)
        group._f_setattr('metadata', building_metadata)
    return

def store_dataset_metadata(metadata,hdf_filename):
    with pd.HDFStore(hdf_filename, 'a') as store_pd:
        store_pd.root._v_attrs.metadata = metadata
        store_pd.close()
    return

def load_meter_devices(yaml_full_filename):
    with open(yaml_full_filename, 'rb') as fh:
        meter_devices = yaml.safe_load(fh)
    return meter_devices

def gen_dataset_metadata(meter_devices_path, start, end):
    end =end.isoformat()
    start=start.isoformat()
    meter_devices=load_meter_devices(meter_devices_path)
    timeframe = {'start':start,'end':end}
    metadata = {}
    metadata['meter_devices'] = meter_devices
    metadata['name'] = 'SHPD'
    metadata['long_name'] = 'Synthetic Heat-Pump Dataset'
    metadata['creator'] = 'Frazer, Benjamin'
    metadata['institution'] = 'The university of Glasgow'
    metadata['number_of_buildings'] = 5
    metadata['time_frame'] = timeframe
    metadata['timezone'] = 'Europe/London'
    metadata['date'] = datetime.now().isoformat()
    metadata['schem'] = 'https://github.com/nilmtk/nilm_metadata/tree/v0.2'
    return metadata

def gen_building_metadata(instance, appliances, elec_meters, timeframe, originalName=None):
    building_metadata = {}
    building_metadata['instance'] =instance
    building_metadata['original_name'] = originalName
    building_metadata['elec_meters'] = elec_meters
    building_metadata['appliances'] = appliances
    building_metadata['timeframe'] = timeframe
    return building_metadata

def gen_hp_appliance_metadata(instance, meters):
    appliance_metadata = {}
    appliance_metadata['type'] = 'heat pump'
    appliance_metadata['instance'] = instance
    appliance_metadata['meters'] = meters
    return appliance_metadata

def gen_hp_meter_metadata(building_instance, key):
    meter_metadata = {}
    meter_metadata['device_model'] = 'hp_generic'
    meter_metadata['submeter_of'] = 0 # submeter of site meter
    meter_metadata['site_meter'] = False
    meter_metadata['data_location'] = str(key)
    return meter_metadata

def gen_hh_meter_metadata(building_instance, key):
    meter_metadata = {}
    meter_metadata['device_model'] = 'hh_generic'
    meter_metadata['submeter_of'] = 0
    meter_metadata['site_meter'] = True
    meter_metadata['data_location'] = str(key)
    return meter_metadata

if __name__ == "__main__":

    from ..config import Paths,hh_filter_config,hp_filter_config, Data
    from ..synthNilmData import filter_stats
    paths = Paths()
    data = Data(paths)

    dateString = datetime.now().strftime("%d-%m-%y")
    output_file = os.getcwd()+f"Test_SHDS_Mixed_{dateString}.hdf5"
    hp_selected = filter_stats(data.hp_stats,hp_filter_config)
    hh_selected = filter_stats(data.hh_stats,hh_filter_config)
    synth_heatpump_agregate_dataset(data.hp_proc_data_store, hp_selected, data.hh_proc_data_store, hh_selected, paths.meter_devices, output_file, targetHouseholds=5, aggregation_level=5)
