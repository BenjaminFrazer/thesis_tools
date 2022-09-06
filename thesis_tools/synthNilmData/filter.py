#!/usr/bin/env ipython
from ..util import Data
import pandas as pd

class Filter :
    data = Data()
    _month_completion_filters = [.90,.90,.90,.90,None,None,None,None,None,None,None,None] # completion for these months must be satisfied
    _months_of_interest_key = "CompMOI"
    _max_sample_period_s = 180
    _sort_by = _months_of_interest_key
    _true_keys = [] # all of these columns must be true
    _false_keys = [] # all of these columns must be false
    _suitible_list = []
    _unsuitible_list = []
    def __init__(self) -> None:
        """Abstract class defining filter properties common to both houshold and heatpump filters."""
        raise NotImplementedError

    def apply(self,stats:pd.DataFrame):
        """
        Filter dataset metrics/stats by the selected filter settings.

        Parameters:
        stats (pd.DataFrame): A dataframe of dataset metrics (assumed to be in the format output in the stats extraction phase).

        Returns:
        pd.DataFrame: A filtered dataframe of dataset metrics per the selected filter parameters.
        """
        stats= stats.copy()
        stats.reset_index(inplace=True)
        suitible = stats['samplePeriod']<=pd.Timedelta(self._max_sample_period_s,"s")
        # filter by completeness of individual months of interest
        count = 0
        average = pd.Series()
        for i,compThresh in enumerate(self._month_completion_filters):
            month = i+1
            monthKey = f"Comp_M{month}"
            if not compThresh is None:
                suitible&=(stats[monthKey]>compThresh)
                count+=1
                average = average.add(stats[monthKey],fill_value=0)
        stats[self._months_of_interest_key] = average.div(count)
        # filter by true keys
        if len(self._true_keys)>0:
            for key in self._true_keys:
                suitible&=stats[key]
        # filter by false key
        if len(self._false_keys)>0:
            for key in self._false_keys:
                suitible&=(~stats[key])
        # filter by suitible list
        if len(self._suitible_list)>0:
            suitible&=(stats["ID"].isin(self._suitible_list))
        #filter by unsutible list
        if len(self._unsuitible_list)>0:
            suitible&=(~stats["ID"].isin(self._unsuitible_list))
        #apply selfer mask
        stats = stats[suitible]
        #sort by selected key
        stats = stats.sort_values(self._sort_by,ascending=False).reset_index(drop=True)
        return stats

class HHFilter(Filter) :
    def __init__(self) -> None:
        self._true_keys = ["isSiteSuitible","isSiteMeter"] # all of these columns must be tru
        known_ht_types = self.data.hh_known_heating_types
        self._unsuitible_list = known_ht_types[known_ht_types["Is Suitable"]==0]["site"].to_list()
        return
hh_filter = HHFilter()

class HPFilter(Filter) :
    def __init__(self) -> None:
        self._suitible_list = self.data.hp_deadband_cat_list
        return
hp_filter = HPFilter()

if __name__ == '__main__':
    import unittest
    cols = ["Pass", "ID",    "isSiteSuitible", "isSiteMeter", "samplePeriod", "Comp_M1", "Comp_M2", "Comp_M3", "Comp_M4", "Comp_M12", "message" ]
    values =  [[True , "IDK13", True,             True,          110,            0.91,      0.91,      0.91,      0.91,      0.2, "should pass                         "], #
               [False, "89773", True,             True,          110,            0.91,      0.91,      0.91,      0.91,      0.2, "blocked by ID in known heating types"], #
               [False, "IDK12", True,             True,          110,            0.91,      0.91,      0.91,      0.88,      0.2, "blocked by completion               "], #
               [False, "IDK12", True,             True,          200,            0.91,      0.91,      0.91,      0.91,      0.2, "blocked by samplerate               "], #
               [False, "IDK12", True,             False,         110,            0.91,      0.91,      0.91,      0.91,      0.2, "blocked by isSitemeter              "], #
               [False, "IDK12", False,            False,         110,            0.91,      0.91,      0.91,      0.91,      0.2, "blocked by isSutible                "]] #
    test_stats_hh = pd.DataFrame(values,columns=cols)
    test_stats_hh["samplePeriod"]=pd.to_timedelta(test_stats_hh["samplePeriod"],unit="s")

    cols = ["Pass", "ID",    "samplePeriod", "Comp_M1", "Comp_M2", "Comp_M3", "Comp_M4", "Comp_M12", "message" ]
    values =  [[True , "HP5524", 110,            0.91,      0.91,      0.91,      0.91,      0.2, "should pass (site is in deadband list)             .  "], #
               [False, "HP5175", 110,            0.91,      0.91,      0.91,      0.91,      0.2, "blocked by ID not in deadband list (wide consistent)  "], #
               [False, "HP5510", 110,            0.91,      0.91,      0.91,      0.91,      0.2, "blocked by ID not in deadband list (other combination)"], #
               [False, "HPDK12", 110,            0.91,      0.91,      0.91,      0.88,      0.2, "blocked by completion                                 "], #
               [False, "HPIK12", 200,            0.91,      0.91,      0.91,      0.91,      0.2, "blocked by samplerate                                 "]] #

    test_stats_hp = pd.DataFrame(values,columns=cols)
    test_stats_hp["samplePeriod"]=pd.to_timedelta(test_stats_hp["samplePeriod"],unit="s")

    stats_filt_hh = hh_filter.apply(test_stats_hh)
    stats_filt_hp = hp_filter.apply(test_stats_hp)
    class TestFiltering(unittest.TestCase):
        def test_filter_hh(self):
            self.assertEqual(1,len(stats_filt_hh))
            self.assertTrue(stats_filt_hh.loc[0,"Pass"])
            return
        def test_filter_hp(self):
            self.assertEqual(1,len(stats_filt_hp))
            self.assertTrue(stats_filt_hp.loc[0,"Pass"])
            return
    unittest.main()
    print(stats_filt_hh)
    print("-----------")
    print(stats_filt_hp)
