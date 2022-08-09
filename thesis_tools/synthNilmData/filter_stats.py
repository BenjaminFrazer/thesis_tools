#!/usr/bin/env ipython
from numpy import average
import pandas as pd
from thesis_tools.config import Filter
from thesis_tools.config import Data
data = Data()
def filter_stats(stats:pd.DataFrame,filt:Filter):
    stats= stats.copy()
    stats = stats.reset_index()
    suitible = stats['samplePeriod']<=pd.Timedelta(filt._max_sample_period_s,"s")
    # filter by completeness of individual months of interest
    count = 0
    average = pd.Series()
    for i,compThresh in enumerate(filt._month_completion_filters):
        month = i+1
        monthKey = f"Comp_M{month}"
        if not compThresh is None:
            suitible&=(stats[monthKey]>compThresh)
            count+=1
            average = average.add(stats[monthKey],fill_value=0)
    stats[filt._months_of_interest_key] = average.div(count)
    # filter by true keys
    if len(filt._true_keys)>0:
        for key in filt._true_keys:
            suitible&=stats[key]
    # filter by false key
    if len(filt._false_keys)>0:
        for key in filt._false_keys:
            suitible&=(~stats[key])
    # import ipdb; ipdb.set_trace()
    # filter by suitible list
    suitible_list = filt.suitible_list
    if len(suitible_list)>0:
        suitible&=stats["ID"].isin(suitible_list)
    #filter by unsutible list
    unsuitible_list = filt.unsuitible_list
    if len(unsuitible_list)>0:
        suitible&=(~stats["ID"].isin(unsuitible_list))
    #apply filter mask
    stats = stats[suitible]
    #sort by selected key
    stats = stats.sort_values(filt._sort_by,ascending=False).reset_index(drop=True)
    return stats

if __name__ == '__main__':
    test_stats_hh = pd.DataFrame([
        {"Pass":True, "ID": "IDK13", "isSiteSuitible":True, "isSiteMeter":True, "samplePeriod":110,"Comp_M1":0.91,"Comp_M2":0.91,"Comp_M3":0.91,"Comp_M4":0.91,"Comp_M12":0.2}, # should pass
        {"Pass":False,"ID": "89773", "isSiteSuitible":True, "isSiteMeter":True, "samplePeriod":110,"Comp_M1":0.91,"Comp_M2":0.91,"Comp_M3":0.91,"Comp_M4":0.91,"Comp_M12":0.2}, # blocked by ID in known heating types
        {"Pass":False,"ID": "IDK12", "isSiteSuitible":True, "isSiteMeter":True, "samplePeriod":110,"Comp_M1":0.91,"Comp_M2":0.91,"Comp_M3":0.91,"Comp_M4":0.88,"Comp_M12":0.2}, # blocked by completion
        {"Pass":False,"ID": "IDK12", "isSiteSuitible":True, "isSiteMeter":True, "samplePeriod":200,"Comp_M1":0.91,"Comp_M2":0.91,"Comp_M3":0.91,"Comp_M4":0.91,"Comp_M12":0.2}, # blocked by samplerate
        {"Pass":False,"ID": "IDK12", "isSiteSuitible":True, "isSiteMeter":False,"samplePeriod":110,"Comp_M1":0.91,"Comp_M2":0.91,"Comp_M3":0.91,"Comp_M4":0.91,"Comp_M12":0.2}, # blocked by isSitemeter
        {"Pass":False,"ID": "IDK12", "isSiteSuitible":False,"isSiteMeter":False,"samplePeriod":110,"Comp_M1":0.91,"Comp_M2":0.91,"Comp_M3":0.91,"Comp_M4":0.91,"Comp_M12":0.2}, # blocked by isSutible
    ])
    test_stats_hh["samplePeriod"]=pd.to_timedelta(test_stats_hh["samplePeriod"],unit="s")
    test_stats_hp = pd.DataFrame([
        {"Pass":True, "ID": "HP5524" , "samplePeriod":110,"Comp_M1":0.91,"Comp_M2":0.91,"Comp_M3":0.91,"Comp_M4":0.91,"Comp_M12":0.2}, # should pass (site is in deadband list)
        {"Pass":False,"ID": "HP5175" , "samplePeriod":110,"Comp_M1":0.91,"Comp_M2":0.91,"Comp_M3":0.91,"Comp_M4":0.91,"Comp_M12":0.2}, # blocked by ID not in deadband list (wide consistent)
        {"Pass":False,"ID": "HP5510" , "samplePeriod":110,"Comp_M1":0.91,"Comp_M2":0.91,"Comp_M3":0.91,"Comp_M4":0.91,"Comp_M12":0.2}, # blocked by ID not in deadband list (other combination)
        {"Pass":False,"ID": "HPDK12", "samplePeriod":110,"Comp_M1":0.91,"Comp_M2":0.91,"Comp_M3":0.91,"Comp_M4":0.88,"Comp_M12":0.2}, # blocked by completion
        {"Pass":False,"ID": "HPIK12", "samplePeriod":200,"Comp_M1":0.91,"Comp_M2":0.91,"Comp_M3":0.91,"Comp_M4":0.91,"Comp_M12":0.2}, # blocked by samplerate
    ])
    test_stats_hp["samplePeriod"]=pd.to_timedelta(test_stats_hp["samplePeriod"],unit="s")
    import unittest
    from thesis_tools.config import hh_filter_config
    from thesis_tools.config import hp_filter_config
    stats_filt_hp = filter_stats(test_stats_hp,hp_filter_config)
    stats_filt_hh = filter_stats(test_stats_hh,hh_filter_config)
    # class TestFiltering(unittest.TestCase):
    #     def test_filter_hh(self):
    #         self.assertEqual(1,len(stats_filt_hh)
    #         self.assertTrue(stats_filt.loc[0,"Pass"])
    #         return
    #     def test_filter_hp(self):
    #         self.assertEqual(1,len(stats_filt_hp))
    #         self.assertTrue(stats_filt_hp.loc[0,"Pass"])
    #         return
    # unittest.main()
    print(stats_filt_hh)
    print("-----------")
    print(stats_filt_hp)
