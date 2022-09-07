#!/usr/bin/env ipython
import git
import os
class Paths :
    _raw_data_dir_full_path = ""
    _this_module_path_rel_2_root = "/../../"
    _interactive_plots_rel_path = "/interactive_plots/"
    _metadata_rel_path = "/metadata/"
    _results_rel_path = "/results/"
    _thesis_tools_rel_path = "/thesis_tools/"
    _hh_known_heating_types_rel_path = _metadata_rel_path+"/hh_known_heating_types.csv"
    _meter_devices_rel_path = _metadata_rel_path+"/meter_devices.yaml"
    _data_dir_rel_path = "/data/"
    _intermediary_data_rel_path = _data_dir_rel_path+"/intermediary/"
    _hh_sitemeter_passlist_rel_path = _metadata_rel_path+"hh_sitemeter_passlist.csv"
    _hh_meter_desc_blocklist_rel_path = _metadata_rel_path+"hh_meter_desc_blocklist.csv"
    _results_overal_pow_agg = _results_rel_path+"res_overal_pow_agg.csv"
    _results_overal_temp_agg_rel_path = []
    _base_synth_data_file_name_fstring = "SHDS_Agg_{x}_08-08-22.hdf5"
    _synth_data_file_names_by_agg_level = {}

    def __init__(self):
        self._results_overal_temp_agg_rel_path= [self._results_rel_path+f"res_overal_temp_agg_pow_{x+1}.csv" for x in range(5)]
        path = os.path.abspath(__file__)
        module_dir_path = os.path.dirname(path)
        self.thesis_tools_root_dir = module_dir_path+self._this_module_path_rel_2_root

    @property
    def res_overall_temp_agg_at_med_pow(self):
        return self.thesis_tools_root_dir+self._results_overal_temp_agg_rel_path[2]
    @property
    def res_overall_temp_agg_at_min_pow(self):
        return self.thesis_tools_root_dir+self._results_overal_temp_agg_rel_path[0]
    @property
    def res_overall_temp_agg_at_max_pow(self):
        return self.thesis_tools_root_dir+self._results_overal_temp_agg_rel_path[-1]
    @property
    def res_overall_temp_agg_at_all_pows(self):
        return [self.thesis_tools_root_dir+self._results_overal_temp_agg_rel_path[x] for x in range(len(self._results_overal_temp_agg_rel_path))]
    @property
    def res_overall_pow_agg(self):
        return self.thesis_tools_root_dir+self._results_overal_pow_agg
    @property
    def interactive_plots_dir(self):
        return self.thesis_tools_root_dir+self._interactive_plots_rel_path

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

    @property
    def synth_data_path(self):
        return self.thesis_tools_root_dir+self._data_dir_rel_path

    @property
    def synth_data_dict(self) -> dict:
        """Returns a dict of strings for each power power aggregation level (index is integer power agg level i.e. 1,2...5)."""
        synth_data_dir = self.synth_data_path
        synth_data_dict_out = {}
        for x in range (1,6):
            synth_data_dict_out[x] = synth_data_dir+self._base_synth_data_file_name_fstring.format(x=x)
            if not os.path.exists(synth_data_dict_out[x]):
                raise FileNotFoundError(f"Could not find file: {synth_data_dict_out[x]} ")
        return synth_data_dict_out

paths = Paths()
