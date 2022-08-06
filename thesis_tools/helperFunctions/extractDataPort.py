#!/usr/bin/env ipython
import os
from nilmtk.dataset_converters.dataport.csv_converter import convert_dataport
import re


dataPortDir = os.getcwd()
outputPath = os.path.join(dataPortDir,"dataport.hdf5")

fileList = []
metadataPath = []
for root, subFolder, files in os.walk(dataPortDir):
    for item in files:
        if re.search('\ds_data_(austin|newyork)_file\d[.]csv', item):
            fileNamePath = str(os.path.join(root,item))
            fileList.append(fileNamePath)
        if re.search('^metadata.csv$',item):
            metadataPath.append(os.path.join(root,item))

print(fileList)
print(metadataPath)
print(outputPath)

metaDataFile = metadataPath[0]
convert_dataport(fileList,metaDataFile,outputPath)
