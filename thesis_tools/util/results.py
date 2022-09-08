#!/usr/bin/env ipython
import pandas as pd
import os
from .paths import Paths
from matplotlib.pyplot import figure
import matplotlib.pyplot as plt
import numpy as np

class Result:
    _results_table = pd.DataFrame()
    _results_file_re = "^.*[Rr]esults.*[.]((hdf5)|(h5))"
    _fileList = []

    def __init__(self, result_path=None):
        if result_path is None:
            self.paths=Paths()
            result_path = self.paths.results
        self._load(result_path)
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

class TestSweep:
    _sweep_summary_df = pd.DataFrame()
    _test_case_name_array = pd.DataFrame()
    _data_avail_array = pd.DataFrame()
    # _test_case_coverage_array = np.array()
    def __init__(self, sweep_summary:str, paths=Paths()):
        self.paths=paths
        self._sweep_summary_df = pd.read_csv(sweep_summary)
        self._populate_TsVsP_arrays()

    def _populate_TsVsP_arrays(self):
        self.uniqueSamplePeriods= self._sweep_summary_df["SamplePeriod(s)"].unique()
        grouped_summary = self._sweep_summary_df[["PowAggLevel","SamplePeriod(s)","ResultsFileName","Itteration"]].groupby("Itteration").first()
        self._test_case_name_array = grouped_summary.pivot(columns="PowAggLevel",index="SamplePeriod(s)",values="ResultsFileName")
        self._data_avail_array = ~self._test_case_name_array.isnull()

    @property
    def available_data(self):
        return self._data_avail_array

    @property
    def sample_periods(self):
        return self.available_data.index.values

    @property
    def power_agg_levels(self):
        return self.available_data.columns.values

    def __getitem__(self, item):
        pass

    def __repr__(self) -> str:
        return repr(self.available_data)

    def plot_predictions_increasing_temporal_agg(self,powerAgg,start:pd.Timestamp,end:pd.Timestamp,disAggAlg2Plot:list):
        # TODO convert to useing kwargs with sensible defaults
        # TODO add option to specify what sample rates to plot predictions for
        # start = pd.Timestamp("2013/04/03 6:30")
        # end =   pd.Timestamp("2013/04/03 12:00")
        # Get valid testcases at this power agg level
        selectedTCs = self.available_data[powerAgg]
        samplePeriods2Test = selectedTCs[~selectedTCs.isnull()].index.values
        figure(figsize=(12, 12), dpi=100)
        fig, axs = plt.subplots(len(disAggAlg2Plot)+1,sharex=True,figsize=(12, 8),)
        plt.subplots_adjust(wspace=0, hspace=0)
        for ii,result_path in samplePeriods2Test:
            with pd.HDFStore(result_path) as store:
                keys = store.keys()
                summary = store["ResultsSummary"]
                res = store[householdKeys[buildingIdx]]
            for i,alg in enumerate(disAggAlg2Plot):
                ax = axs[i]
                toplot = res.loc[start:end,alg]["heat pump"].rename(f"Sample Period :{samplePeriods2Test[ii]}")
                if ii == 0:
                    ax.text(0.95, 0.85,alg, ha='center', va='center', transform=ax.transAxes).set_bbox(dict(facecolor='w',alpha=0.9))
                    toplot_gt = res.loc[start:end,"GroundTruth"]["heat pump"].rename("GT")
                    toplot_gt.plot(ax=ax,color="k")
                toplot.plot(ax=ax,style="--",lw=1.5);
                # if ii != len(results_names)-1:
                #     ax.xaxis.set_ticklabels([])

            ax = axs[-1]
            if ii==0:
                toplot_gt = res.loc[start:end,"GroundTruth"]["heat pump"].rename("GT")
                toplot_gt.plot(ax=ax,color="k")
            next(dataset.buildings[buildingIdx+1].elec[1].load(sample_period=samplePeriods2Test[ii]))["power"]["active"].rename(f"Sitemeter, Sample Period:{samplePeriods2Test[ii]}").plot(legend=False)
            ax.text(0.9, 0.85,"Sitemeter (Aggregated)", ha='center', va='center', transform=ax.transAxes).set_bbox(dict(facecolor='w',alpha=0.9))
        leg = ["GT"]+[f"Ts:{x}s" for x in samplePeriods2Test]
        axs[1].legend(leg,loc=(1.01, 0.9));
        axs[1].set_ylabel("Power (W)");
        axs[-1].set_xlabel("Time (Date)");
