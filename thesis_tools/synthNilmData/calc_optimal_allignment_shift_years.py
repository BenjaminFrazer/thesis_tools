#!/usr/bin/env ipython
from synthNilmData.get_month_spans import get_month_spans
import numpy as np
import pandas as pd
def calc_optimal_allignment_shift_years(months_of_interest,span1,span2):
    # calculate the time shift in years to apply to span 2 to bring it into optimal alignment with span 1
    years1, completeness1, spans = get_month_spans(months_of_interest,span1[0],span1[1])
    years2, completeness2, spans = get_month_spans(months_of_interest,span2[0],span2[1])
    conv = np.correlate(completeness2,completeness1,mode="full")
    startYearDiff = years2[0] - years1[0]
    shiftMax =conv.argmax()
    shift = -len(completeness2)+1+shiftMax-startYearDiff
    return shift

if __name__ == "__main__":
    timeSpans= [
    [pd.Timestamp("2019/02/01"), pd.Timestamp("2021/04/01")],
    [pd.Timestamp("2014/01/01"), pd.Timestamp("2014/01/11")],
    [pd.Timestamp("2013/04/15"), pd.Timestamp("2014/07/01")],
    [pd.Timestamp("2012/03/29"), pd.Timestamp("2015/03/04")],]

    print(calc_optimal_allignment_shift_years([1,3],timeSpans[0],timeSpans[1]))
