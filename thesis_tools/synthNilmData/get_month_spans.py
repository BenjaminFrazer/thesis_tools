#!/usr/bin/env ipython
import numpy as np
import pandas as pd
def get_month_spans(monthsOfInterest,start,end):
    tz_start = str(start.tz)
    tz_end = str(end.tz)
    assert tz_start == tz_end
    nMonths = monthsOfInterest[1]-monthsOfInterest[0]
    timeDeltaMonths= np.timedelta64(nMonths+1,"M")
    start_year = start.year
    end_year = end.year
    spans = []
    completeness = []
    years = []
    for thisyear in range(start_year,end_year+1):
        if tz_start == "None":
            thisYearTargetMonthStartTs =pd.Timestamp(year=thisyear,month=monthsOfInterest[0],day=1)
        else:
            thisYearTargetMonthStartTs =pd.Timestamp(year=thisyear,month=monthsOfInterest[0],day=1,tz=tz_end)
        thisYearTargetMonthEndTs=thisYearTargetMonthStartTs+timeDeltaMonths
        if (thisYearTargetMonthEndTs>=start) & (thisYearTargetMonthStartTs<=end):
            years.append(thisyear)
            spanStart = max(thisYearTargetMonthStartTs,start)
            spanEnd = min(thisYearTargetMonthEndTs,end)
            span= spanEnd - spanStart
            completeness.append(round(span/timeDeltaMonths,4))
            spans.append({"start":spanStart,"end":spanEnd})

    return (years, completeness, spans)

if __name__ == "__main__":
    start = pd.Timestamp("2021/01/15")
    end = pd.Timestamp("2023/02/15")
    span = [1,3]
    print(get_month_spans(span,start,end))
