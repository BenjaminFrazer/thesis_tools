#!/usr/bin/env ipython
from .paths import Paths
import pandas as pd

class Data :

    paths:Paths
    def __init__(self,paths=None):
        """
        Contains getters for data which has been stored on disk.

        Parameters:
        paths (Paths): Object containing paths to stored data

        Returns:
        int: Description of return value.

        """
        if paths is None:
            paths = Paths()
        self.paths = paths

    @property
    def hp_proc_data_store(self):
        """Get the heat pump pre-processed .hdf5 data store"""
        return pd.HDFStore(self.paths.hp_proc_data_store)

    @property
    def hh_proc_data_store(self):
        """Get the household pre-processed .hdf5 data store"""
        return pd.HDFStore(self.paths.hh_proc_data_store)

    @property
    def hh_stats(self):
        """Get the household dataset metrics"""
        return pd.read_hdf(self.paths.hh_proc_stats_store)

    @property
    def hp_stats(self):
        """Get the heatpump dataset metrics"""
        return pd.read_hdf(self.paths.hp_proc_stats_store)

    @property
    def hp_load_profile_categories(self):
        """Get the heatpump load profile cattegories (from .csv file)"""
        return pd.read_csv(self.paths.hp_load_profile_categories)

    @property
    def hh_known_heating_types(self):
        """Get the household load profile known/suspected heating type list"""
        return pd.read_csv(self.paths.hh_known_heating_types)

    @property
    def hp_deadband_cat_list(self):
        """Get only the deadband heatpump load profile IDs (as a list)"""
        hp_deadband_ls = list(self.hp_load_profile_categories["Deadband"].dropna().astype(int))
        return [f"HP{x}" for x in hp_deadband_ls]

    @property
    def synth_data_list(self):
        """Get the household load profile known/suspected heating type list"""
        self.paths.synth_data_path
        return pd.read_csv(self.paths.hh_known_heating_types)

data = Data()
