#!/usr/bin/env ipython
import pandas as pd
import matplotlib.pyplot as plt
import warnings
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

from hashlib import md5

from IPython.display import Image, FileLink, display

import plotly.graph_objects as go
import plotly.io as pio
# from ..config import Paths
# paths = Paths()
def plot_sample_loadprofile(stats: pd.DataFrame, offset_d: int, span_d: int, datastore_path: str) -> None:
    stats = stats[~stats["empty"]].reset_index()
    IDs = list(stats["ID"])
    with pd.HDFStore(datastore_path) as h5:
        df = pd.concat(map(h5.get, IDs), axis=1)
    df.columns = IDs
    # import warnings
    # warnings.filterwarnings("ignore")
    nplots = len(stats)
    fig, axs = plt.subplots(nplots)
    plt.subplots_adjust(wspace=0, hspace=0)
    for i in range(nplots):
        ID = stats.loc[i,"ID"]
        start = stats.loc[i,"start"]+pd.Timedelta(offset_d,"D")
        end = start+pd.Timedelta(span_d,"D")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df.loc[start:end,ID].plot(ax=axs[i],legend=ID).legend(loc="upper right")
        if i +1 < nplots:
            axs[i].axes.xaxis.set_ticklabels([])
    plt.show()
    return fig

def plot_sample_loadprofile_noshift(stats: pd.DataFrame, start, end, datastore_path: str) -> None:
    stats = stats[~stats["empty"]].reset_index()
    IDs = list(stats["ID"])
    with pd.HDFStore(datastore_path) as h5:
        df = pd.concat(map(h5.get, IDs), axis=1)
    df.columns = IDs
    # import warnings
    # warnings.filterwarnings("ignore")
    nplots = len(stats)
    fig, axs = plt.subplots(nplots)
    plt.subplots_adjust(wspace=0, hspace=0)
    for i in range(nplots):
        ID = stats.loc[i,"ID"]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df.loc[start:end,ID].plot(ax=axs[i],legend=ID).legend(loc="upper right")
        if i +1 < nplots:
            axs[i].set_xticks([],[])
    plt.show()
    return fig

def plotly_sample_load_profiles(stats :pd.DataFrame, offset_d:int, span_d:int, datastore_path:str, output_filename:str):
    import warnings
    warnings.filterwarnings("ignore")
    nplots = len(stats)
    fig = make_subplots(rows=len(stats),cols=1,shared_xaxes=True)
    plt.subplots_adjust(wspace=0, hspace=0)
    common_index = pd.Series() # make the lsp happy
    for i in range(nplots):
        ID = stats.loc[i,"ID"]
        with pd.HDFStore(datastore_path) as h5:
            thisSeries=h5[ID]
        start = stats.loc[i,"start"]+pd.Timedelta(offset_d,"D")
        end = start +pd.Timedelta(span_d,"D")
        thisSeries = thisSeries[start:end]
        if i == 0:
            common_index = thisSeries.index
        fig.append_trace(go.Scatter(x=common_index,y=thisSeries,name=ID), row=i+1, col=1)
    fig.show(fileName=output_filename)

def myshow(self, *args, **kwargs):
    """Display function specific to displaying plotly figures within an orgmode buffer."""
    fhtml = kwargs.pop("fileName",None)
    html = pio.to_html(self)
    if fhtml is None:
        mhash = md5(html.encode('utf-8')).hexdigest()
        if not os.path.isdir('.ob-jupyter'):
            os.mkdir('.ob-jupyter')
        fhtml = os.path.join('.ob-jupyter', mhash + '.html')

    with open(fhtml, 'w') as f:
        f.write(html)

    display(FileLink(fhtml, result_html_suffix=''))
    return Image(pio.to_image(self, 'png'))

def plotly_sample_load_profiles_noshift(selected_stats, start, end, datastore_path, output_filename ):
    import warnings
    warnings.filterwarnings("ignore")
    nplots = len(selected_stats)
    fig = make_subplots(rows=len(selected_stats),cols=1,shared_xaxes=True)
    for i in range(nplots):
        ID = selected_stats.loc[i,"ID"]
        with pd.HDFStore(datastore_path) as h5:
            thisSeries=h5[ID]
        thisSeries = thisSeries[start:end]
        fig.append_trace(go.Scatter(x=thisSeries.index,y=thisSeries,name=ID), row=i+1, col=1)
    fig.show(fileName=output_filename)

go.Figure.show = myshow
