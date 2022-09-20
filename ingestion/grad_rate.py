import pandas as pd
import seaborn as sns
from argparse import ArgumentError
import numpy as np

urls = ("https://www2.ed.gov/about/inits/ed/edfacts/data-files/acgr-sch-sy2010-11.csv", \
        "https://www2.ed.gov/about/inits/ed/edfacts/data-files/acgr-sch-sy2011-12.csv", \
        "https://www2.ed.gov/about/inits/ed/edfacts/data-files/acgr-sch-sy2012-13.csv", \
        "https://www2.ed.gov/about/inits/ed/edfacts/data-files/acgr-sch-sy2013-14.csv", \
        "https://www2.ed.gov/about/inits/ed/edfacts/data-files/acgr-release2-sch-sy2014-15.csv", \
                "https://www2.ed.gov/about/inits/ed/edfacts/data-files/acgr-sch-sy2015-16.csv",  \
                "https://www2.ed.gov/about/inits/ed/edfacts/data-files/acgr-sch-sy2016-17.csv",  \
                "https://www2.ed.gov/about/inits/ed/edfacts/data-files/acgr-sch-sy2017-18.csv",  \
                "https://www2.ed.gov/about/inits/ed/edfacts/data-files/acgr-sch-sy2018-19-wide.csv")
def make_raw_gr_frame(year):
    """ Create raw graduation rate dataframe for a given year directly from the .csv url. It is 'raw' because 
    no modifications like renaming or deleting are done. """ 
    # Verify input parameter is valid
    if year not in list(range(2010,2019)):
        raise ArgumentError("input parameter (year) must be between 2010 and 2018") 
    return pd.read_csv(urls[year-2010])

def _column_renamer(year, colname): 
    """ Takes an inputted column name string and returns one with with suffixes removed"""
    suffix0 = "_" + str(year)[-2:] + str(int(str(year)[-2:])+1)
    suffix1 = "COHORT" + suffix0
    colname = colname.removesuffix(suffix1).removesuffix(suffix0)
    if colname.endswith('_'):
        colname = colname.removesuffix('_')
    return colname

def make_gr_frame(year):
    """ Takes in the year as a parameter and returns a cleaned up dataframe.
        Some columns are dropped and strings are converted to numbers.
        Each of the subpopulations (e.g. ALL for all the kids or MTR for multi-racial kids) has
        two columns, one with the total number of kids who *could have* graduated,
        and one ending in RATE which is the percentage of them that did graduate.
     """
    df = make_raw_gr_frame(year)
    # Drop un-needed columns
    df.drop(labels=['FIPST', 'LEANM', 'LEAID','DATE_CUR'],axis='columns',inplace=True)
    # Rename columns so the names are shorter
    new_col_names = list(map(_column_renamer,[year]*len(df.columns),df.columns))
    df.columns = new_col_names
    return clean_all_rate(df)

def conv_range_to_float(t: str):
    """ Take in a numeric range given as a string, e.g. "10-20" and return the midpoint as a float. """
    vals = t.split('-')
    if len(vals) == 2:
        val1,val2 = np.float64(vals)
        return round(val1/2.0 + val2/2.0, 0)
    else:
        return t

def clean_all_rate(df : pd.DataFrame):
    """ Drop rows with missing values for the ALL or ALL_RATE columns. Convert strings to numbers. 
    Small number of schools are missing an ALL_RATE. Suppressed RATE data for 1-5 students are reported as 'PS'
    Some rates have a prefix of GT, GE, LT, or LE.
    """
    # Drop schools with no value given for the number of total kids.
    df.loc[:,:] = df[df.ALL != "."]
    # Drop small schools that have less than 5 total students in their cohort because no rate is given for them.
    df.loc[:,:] = df[df.ALL_RATE != "PS"]
    df.dropna(subset=['NCESSCH', 'ALL','ALL_RATE'],inplace=True)
    # Prefixes are given for the graduation rates that mean "greater than", "less than", etc. to make it hard to identify
    # individual children when the cohorts are small. 
    # Strip off prefixes and use the range endpoint as an approximation for the grad rate.
    prefixes = ['GT','LT','GE','LE']
    colname = 'ALL_RATE'
    df.loc[:, colname] = df[colname].str.removeprefix('GE')
    df.loc[:, colname] = df[colname].str.removeprefix('LE')
    df.loc[:, colname] = df[colname].str.removeprefix('GT')
    df.loc[:, colname] = df[colname].str.removeprefix('LT')

    df.loc[:,'ALL_RATE2'] = df.ALL_RATE.transform(conv_range_to_float)

    df.loc[:,'ALL'] = pd.to_numeric(df.ALL)
    df.loc[:,'ALL_RATE2'] = pd.to_numeric(df.ALL_RATE2)
    
    df.loc[:,'ALL_RATE'] = df.ALL_RATE2
    df.drop(labels='ALL_RATE2',axis=1,inplace=True) 

    assert((sum(df.ALL == '.'), sum(df.ALL_RATE == 'PS')) == (0, 0))
    return df
