#!/usr/bin/env ipython
import git

class Paths :
    _data_dir_full_path = "/home/benjaminf/data"

    _hh_xls_rel_path = "/household/extract_ReFLEX.xlsx"

    _hh_known_heating_types_rel_path = "/python/synthNilmData/hh_known_heating_types.csv"

    _meter_devices_rel_path = "/python/synthNilmData/metadata/meter_devices.yaml"
    code_rel_path = "/python/"
    _synth_data_rel_path = "/python/synthNilmData/"


    def __init__(self,thesisDir = None):
        if thesisDir is None:
            repo = git.Repo('.', search_parent_directories=True)
            thesisDir=repo.working_tree_dir
        self.root_dir = thesisDir

    @property
    def synth_data_path(self):
        return self.root_dir+self._synth_data_rel_path

    @property
    def meter_devices(self):
        return self.root_dir+self._meter_devices_rel_path

    @property
    def hpRawDataMat(self):
        return self._data_dir_full_path+"/heat_pump/UK_HeatPump_Data_2013_2015/Cleaned_Energy_Data.mat.mat"

    @property
    def hhRawDataDir(self):
        return self._data_dir_full_path+"/household/2021/"

    @property
    def hh_known_heating_types(self):
        return self.root_dir+self._hh_known_heating_types_rel_path

    @property
    def hh_proc_data_store(self):
        return self.root_dir+"/python/synthNilmData/proc_hh_data.hdf5"

    @property
    def hh_proc_stats_store(self):
        return self.root_dir+"/python/synthNilmData/hh_data_stats.hdf5"

    @property
    def hp_proc_data_store(self):
        return self.root_dir+"/python/synthNilmData/proc_hp_data.hdf5"

    @property
    def hp_proc_stats_store(self):
        return self.root_dir+"/python/synthNilmData/hp_data_stats.hdf5"

# paths = Paths()
