#!/usr/bin/env ipython
import pandas as pd
import numpy as np
import os.path as path
import os
import re
import regex
from datetime import datetime
import warnings
from tables import NaturalNameWarning
# we don't plan on using table accessing in the data store so we dont need to respect natural naming
warnings.filterwarnings('ignore', category=NaturalNameWarning)

def process_raw_household_data(dataDirPath,dataOut,siteMeterPassList=None,siteSuitibilityColDescBlockList=None, debug=True, TZ='Europe/London'):
    # walk the filepath and look for data that matches the path
    hhDataFiles = []
    for dirpath, dirnames, filenames in os.walk(dataDirPath):
        for thisFile in filenames:
            if re.match("^[0-9_a-zA-Z]{8,13}[.]csv$",thisFile):
                fullpath = path.join(dirpath,thisFile)
                hhDataFiles.append(fullpath)

    # Build Pass list RE
    if siteMeterPassList != None:
        passRe_or = ""
        for passItem in siteMeterPassList:
            passRe_or+=f"(\s?{passItem}\s?)|"
        passRe_or=passRe_or[:-1] #trim off last element
    else:
        passRe_or = ".*"

    #Build site suitibility block list RE
    if siteSuitibilityColDescBlockList != None:
        blockRe_or = ""
        for blockItem in siteSuitibilityColDescBlockList:
            blockRe_or+=f"(.*{blockItem}.*)|"
        blockRe_or=blockRe_or[:-1] #trim off last element
    else:
        blockRe_or = "$^" # this will intentionaly match nothing and thus block nothing!


    # build dataframe
    sr = pd.DataFrame()
    reColumnDescriptors = r"(?<=[(])\s?[a-zA-Z 0-9_+(]*\s?(?=[)]+\s?$)"
    reSid= r"(?<=sid ?= ?)\d{6}"
    reHouseId= r"^[A-Z0-9]{4,5}(?=_?[A-Za-z]{3}[0-9]{0,4}[.]csv)"
    # this might be more rows than nececery but this is ok
    #
    stats = pd.DataFrame({'ID': pd.Series(dtype='int'),
                          'meterDesc': pd.Series(dtype='str'),
                          'isSiteSuitible': pd.Series(dtype='bool'),
                          'isSiteMeter': pd.Series(dtype='bool')},
                         )
    stats = stats.set_index('ID')

    IDs = set()# will be appended to
    for filename in hhDataFiles:
        # if re.match(".*FEB.*",filename):
        #     import pdb; pdb.set_trace()
        basename = os.path.basename(filename)

        # print(f"loading {basename}")
        ID_match = re.match(reHouseId,basename)
        assert ID_match
        ID = ID_match.group(0)
        thishh_df = (pd.read_csv(filename,index_col='Timestamp',parse_dates=['Timestamp'],dayfirst=False))
        try:
            thishh_df.index = thishh_df.index - pd.DateOffset(hours=1)
            thishh_df.index = thishh_df.index.tz_localize('UTC').tz_convert(TZ)
        except:
            import pdb; pdb.set_trace()

        columnHeadings = list(thishh_df.columns)
        columnDescString = [re.search(reColumnDescriptors,x).group() if re.search(reColumnDescriptors,x) else "" for x in columnHeadings]
        sid = [regex.search(reSid,x).group() if regex.search(reSid,x) else "" for x in columnHeadings]

        # test if a column exists
        if ID in IDs:# we've already got an entry in stats
            thisSitemeterSid = stats.loc[ID,'sid'] # we have already decided on the sitemeter for this dataset in prior loops
            with pd.HDFStore(dataOut) as store:
                sr = store[ID]
        else:
            IDs.add(ID)
            # test the blocklist first
            suitible = not any(re.match(blockRe_or,x) for x in columnDescString)

            # now locate the site meter
            matches = [True if re.search(passRe_or,x) else False for x in columnDescString]
            if matches.count(True) >1:
                if debug:
                    print(f"Multiple Candidate Site Meters taking 1st col, ID:{ID[-1]}, Col Desc:{columnDescString}, Headings:{columnHeadings}")
                siteMeterFound=True
                sitemeterIdx = matches.index(True)
            elif matches.count(True) ==0:
                if debug:
                    print(f"Site Meter Not Found taking 1st col, ID:{ID[-1]}, Col Desc:{columnDescString}, Headings:{columnHeadings}")
                siteMeterFound = False
                sitemeterIdx = 0 # this is usualy the first data column
            else:
                sitemeterIdx = matches.index(True)
                siteMeterFound = True

            thisSitemeterSid = sid[sitemeterIdx]# we have already decided on the sitemeter for this dataset in prior loops

            this_stats = pd.DataFrame({
                                    "meterDesc":columnDescString[sitemeterIdx],
                                    "sid":thisSitemeterSid,
                                    "isSiteMeter":siteMeterFound,
                                    "isSiteSuitible":suitible},
                                    [ID])
            this_stats.index.name = "ID"
            stats = pd.concat([stats, this_stats],axis=0,sort=True)
            sr = pd.Series()

        idxSiteMeterSid = sid.index(thisSitemeterSid) # this gives us a column index for the site id we need to find
        sitemeterCol= columnHeadings[idxSiteMeterSid]
        # thisData2Concat = thishh_df[[sitemeterCol]].rename(columns={sitemeterCol:ID}) # we rename the column to the ID

        # add to the household dataframe
        sr = pd.concat([sr,thishh_df[sitemeterCol]],axis=0,sort=True)
        assert isinstance(sr,pd.Series)

        with pd.HDFStore(dataOut) as store:
            store[ID] = sr

    with pd.HDFStore(dataOut) as store: # here we need to sort and clean up the data
        for key in store.keys():
            ID = key.replace("/","")
            this_df = store[key].copy()
            this_df = this_df[~this_df.index.duplicated()]
            this_df.sort_index(ascending=True,inplace=True)
            store.put(ID,this_df)
    return stats


if __name__ == "__main__":
#test the function
    blocklist = ["Car","car","Solar","solar","Heapump","Wind","Turbine","generation"]
    passlist = ["Whole house","Whole House","whole house","Whole Property","whole property","House Supply","house supply"]
    hhDataFilePath = "/home/benjaminf/data/household/"
    stats, hh = process_raw_household_data(hhDataFilePath, passlist, blocklist)
    print(stats)
    print(hh)
