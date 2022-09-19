import pandas as pd
import seaborn as sns
from argparse import ArgumentError

urls = ("https://www2.ed.gov/about/inits/ed/edfacts/data-files/acgr-sch-sy2010-11.csv", \
        "https://www2.ed.gov/about/inits/ed/edfacts/data-files/acgr-sch-sy2011-12.csv", \
        "https://www2.ed.gov/about/inits/ed/edfacts/data-files/acgr-sch-sy2012-13.csv", \
        "https://www2.ed.gov/about/inits/ed/edfacts/data-files/acgr-sch-sy2013-14.csv", \
        "https://www2.ed.gov/about/inits/ed/edfacts/data-files/acgr-release2-sch-sy2014-15.csv", \
                "https://www2.ed.gov/about/inits/ed/edfacts/data-files/acgr-sch-sy2015-16.csv",  \
                "https://www2.ed.gov/about/inits/ed/edfacts/data-files/acgr-sch-sy2016-17.csv",  \
                "https://www2.ed.gov/about/inits/ed/edfacts/data-files/acgr-sch-sy2017-18.csv",  \
                "https://www2.ed.gov/about/inits/ed/edfacts/data-files/acgr-sch-sy2018-19-long.csv")

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
    # @TODO Converting string data to numbers
    # Small number of schools are missing an ALL rate
    # Suppressed RATE data for 1-5 students are reported as 'PS'
    # Some rates have a prefix of GT, GE, LT, or LE
    return df 
