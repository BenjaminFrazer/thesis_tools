#!/usr/bin/env ipython
import git
import os
import pandas as pd

class Paths :
    _raw_data_dir_full_path = "/home/benjaminf/data/"
    code_rel_path = "/python/"
    _synth_data_rel_path = "/python/synthNilmData/"
    _this_module_path_rel_2_root = "/../../"
    _interactive_plots_rel_path = "/interactive_plots/"
    _metadata_rel_path = "metadata"
    _results_rel_path = "results"
    _thesis_tools_rel_path = "thesis_tools"
    _hh_known_heating_types_rel_path = _metadata_rel_path+"/hh_known_heating_types.csv"
    _meter_devices_rel_path = _metadata_rel_path+"/meter_devices.yaml"
    _data_dir_rel_path = "/data/"
    _intermediary_data_rel_path = _data_dir_rel_path+"/intermediary/"
    _hh_sitemeter_passlist_rel_path = _metadata_rel_path+"hh_sitemeter_passlist.csv"
    _hh_meter_desc_blocklist_rel_path = _metadata_rel_path+"hh_meter_desc_blocklist.csv"

    def __init__(self,thesisDir = None):
        if thesisDir is None:
            repo = git.Repo('.', search_parent_directories=True)
            thesisDir=repo.working_tree_dir
        self.root_dir = thesisDir
        path = os.path.abspath(__file__)
        module_dir_path = os.path.dirname(path)
        # import pdb; pdb.set_trace()
        self.thesis_tools_root_dir = module_dir_path+self._this_module_path_rel_2_root

    @property
    def synth_data_path(self):
        return self.thesis_tools_root_dir+self._synth_data_rel_path

    @property
    def meter_devices(self):
        return self.thesis_tools_root_dir+self._meter_devices_rel_path

    @property
    def hpRawDataMat(self):
        return self._raw_data_dir_full_path+"/heat_pump/UK_HeatPump_Data_2013_2015/Cleaned_Energy_Data.mat.mat"

    @property
    def hhRawDataDir(self):
        return self._raw_data_dir_full_path+"/household/2021/"

    @property
    def hh_known_heating_types(self):
        return self.thesis_tools_root_dir+self._hh_known_heating_types_rel_path

    @property
    def hh_proc_data_store(self):
        return self.thesis_tools_root_dir+self._intermediary_data_rel_path+"/proc_hh_data.hdf5"

    @property
    def hh_proc_stats_store(self):
        return self.thesis_tools_root_dir+self._intermediary_data_rel_path+"/hh_data_stats.hdf5"

    @property
    def hp_proc_data_store(self):
        return self.thesis_tools_root_dir+self._intermediary_data_rel_path+"/proc_hp_data.hdf5"

    @property
    def hp_proc_stats_store(self):
        return self.thesis_tools_root_dir+self._intermediary_data_rel_path+"/hp_data_stats.hdf5"

    @property
    def results(self):
        return self.thesis_tools_root_dir+self._results_rel_path

    @property
    def hp_load_profile_categories(self):
        return self.thesis_tools_root_dir+self._metadata_rel_path+"/hp_load_profile_categories.csv"


class Data :
    def __init__(self,paths=None):
        if paths is None:
            self.paths = Paths()

    @property
    def hp_proc_data_store(self):
        return pd.HDFStore(self.paths.hp_proc_data_store)

    @property
    def hh_proc_data_store(self):
        return pd.HDFStore(self.paths.hp_proc_data_store)

    @property
    def hh_stats(self):
        return pd.read_hdf(self.paths.hh_proc_stats_store)

    @property
    def hp_stats(self):
        return pd.read_hdf(self.paths.hh_proc_stats_store)

    @property
    def hp_load_profile_categories(self):
        return pd.read_csv(self.paths.hp_load_profile_categories)

    @property
    def hh_known_heating_types(self):
        return pd.read_csv(self.paths.hh_known_heating_types)

    @property
    def hh_unsuitible_list(self):
        suitibility_list = list(self.hh_known_heating_types[self.hh_known_heating_types["Is Suitable"]!=1]["site"])
        return suitibility_list

    @property
    def hp_deadband_cat_list(self):
        hp_deadband_ls = list(self.hp_load_profile_categories["Deadband"].dropna().astype(int))
        return [f"HP{x}" for x in hp_deadband_ls]

class Results :
    _results_table = pd.DataFrame()
    _results_file_re = "^.*[Rr]esults.*[.]((hdf5)|(h5))"
    _fileList = []

    def __init__(self, results_path=None):
        if results_path is None:
            self.paths=Paths()
            results_path = self.paths.results
        self._load(results_path)
        return

    def _load(self,results_path):
        import re
        self._fileList = []
        files = next(os.walk(results_path))[2]
        for item in files:
            if re.search(self._results_file_re, item):
                fileNamePath = str(os.path.join(results_path,item))
                self._fileList.append(fileNamePath)
        return

    def __getitem__(self, item):
        return pd.HDFStore(self._fileList[item])

    def __repr__(self) -> str:
        baseNames = [os.path.basename(x) for x in self._fileList]
        return str(baseNames)

class Filter :
    data = Data()
    #                              J  F  M  A   M   J    J    A    S    O    N     D
    _month_completion_filters = [.90,.90,.90,.90,None,None,None,None,None,None,None,None] # completion for these months must be satisfied
    _months_of_interest_key = "CompMOI"
    _max_sample_period_s = 180
    _sort_by = _months_of_interest_key
    _true_keys = [] # all of these columns must be tru
    _false_keys = [] # all of these columns must be false
    suitible_list = []
    unsuitible_list = []

class HHFilter(Filter) :
    # maybe in future this can take a profile defined in a jason?
    def __init__(self) -> None:
        self._true_keys = ["isSiteSuitible","isSitemeter"] # all of these columns must be tru
        self.unsuitible_list = self.data.hh_unsuitible_list
        return
hh_filter_config = HHFilter()

class HPFilter(Filter) :
    # maybe in future this can take a profile defined in a jason?
    def __init__(self) -> None:
        self.suitible_list = self.data.hp_deadband_cat_list
        return
hp_filter_config = HPFilter()
