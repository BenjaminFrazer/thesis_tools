#!/usr/bin/env ipython
from IPython.display import display
import sys, os

# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__


def printDatasetApplianceInfo(_dataset):
    trueFalseLUT = {True:"T", False:"F"}
    thisTable=[]
    tableHeading = ["Building", "Start", "End", "nHP", "nAC", "nHT", "nEV","Ts(s)", "P", "Q", "S", "I", "V","P_sm","Q_sm","S_sm"]
    thisTable.append(tableHeading)
    thisTable.append(None)
    for i in range(1,len(_dataset.buildings)+1):
        _startStr= _dataset.buildings[i].elec.get_timeframe().start.strftime("%d/%m/%Y")
        _endStr = _dataset.buildings[i].elec.get_timeframe().end.strftime("%d/%m/%Y")
        nActive =0;nReactive=0;nApparent=0
        # loop through all non site meters and store the available channels
        blockPrint() # suppress printing here because accessing meters sometimes prints unwanted info messages
        listAvailACTypes = []
        for ii in range(len(_dataset.buildings[i].elec.meters)):
            if not _dataset.buildings[i].elec.meters[ii].is_site_meter():
                theseACtypes = _dataset.buildings[i].elec.meters[ii].available_ac_types('power')
                listAvailACTypes.append(theseACtypes)
                nActive += theseACtypes.count('active')
                nReactive += theseACtypes.count('reactive')
                nApparent += theseACtypes.count('apparent')
        enablePrint()
        P_sm = nActive
        S_sm = nApparent
        Q_sm = nReactive

        # loop through all site meters and store the sample rate rate
        _powerTypes = _dataset.buildings[i].elec.mains().available_ac_types(["power"])
        _samplePeriod = _dataset.buildings[i].elec.sample_period()
        V = trueFalseLUT[len(_dataset.buildings[i].elec.mains().available_ac_types(["voltage"]))!=0]
        I = trueFalseLUT[len(_dataset.buildings[i].elec.mains().available_ac_types(["current"]))!=0]
        P = trueFalseLUT["active" in _powerTypes]
        S = trueFalseLUT["apparent" in _powerTypes]
        Q = trueFalseLUT["reactive" in _powerTypes]

        nHP = 0;nHT = 0;nEV = 0;nAC= 0
        for ii in range(len(_dataset.buildings[i].elec.appliances)):
            _thisLable=_dataset.buildings[i].elec.appliances[ii].metadata.get("type")
            if _thisLable == 'electric space heater' or _thisLable == 'electric furnace':
                nHT+=1
            elif _thisLable=='heat pump':
                nHP+=1
            elif _thisLable == 'air conditioner':
                nAC+=1
            elif _thisLable == 'electric vehicle':
                nEV+=1
        _thisRow = [i,_startStr,_endStr,nHP,nAC,nHT,nEV, _samplePeriod,P,Q,S,I,V,P_sm,Q_sm,S_sm]
        thisTable.append(_thisRow)
    display(thisTable)

# dataDir = '/home/benjaminf/data/'

# from nilmtk import DataSet

# redd = DataSet(dataDir+'/redd/redd.h5')
# ukdale = DataSet(dataDir+'/ukdale/ukdale.h5')

# printDatasetApplianceInfo(ukdale)
# class Test_printDatasetApplianceInfo(unittest.TestCase):
#     def test_print():
