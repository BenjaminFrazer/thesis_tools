#!/usr/bin/env ipython
from synthNilmData import get_month_spans
def completeness_in_months_of_interest(stats_df,monthsOfInterest):
    def _completionInRegionOfInterest(*args):
        if any(isinstance(x,float) for x in args):
            return 0.0
        completion = get_month_spans(*args)[1]
        if len(completion)==0:
            return 0.0
        else:
            return max(completion)
    return stats_df.apply(lambda x: _completionInRegionOfInterest(monthsOfInterest,x["start"],x["end"]), axis=1)
