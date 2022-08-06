#!/usr/bin/env ipython
from nilmtk import DataSet
import matplotlib.pyplot as plt
hdf_filename = 'SHPD.hdf5'
hpds= DataSet(hdf_filename)
hpds.set_window(start='2021-09-01', end='2021-09-11')
ax = hpds.buildings[1].elec.plot()
ax.show()
