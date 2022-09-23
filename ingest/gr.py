"""
1. Trim prefixes
1. Replace ranges with average
1. Replace PS with NaN
1. Convert to numeric
1. Drop NaNs
1. Verify IQR's are reasonable
"""
import sys,os
sys.path.append(os.getcwd() + '/..')
import pandas as pd
import numpy as np
import shelve

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
        raise ValueError("input parameter {} is out of range.".format(year))
    return pd.read_csv(urls[year-2010])

def conv_range_to_float(t: str):
    """ Take in a numeric range given as a string, e.g. "10-20" and return the midpoint as a float. """
    vals = t.split('-')
    if len(vals) == 2:
        val1,val2 = float(vals[0]), float(vals[1])
        return val1/2.0 + val2/2.0
    else:
        return t


def year_string(y : int):
    """ Input an integer year and get a range that matches the column suffixes in the raw data.
    e.g. 2011 => 1112 and 2018 => 1819."""
    return str(y)[-2:] + str(int(str(y)[-2:])+1)


def make_total_cohort_frame(in_year):
    """ Takes in a valid year. Returns a dataframe with identifiers for the school,
    the size of the cohort, and the graduation rate. """
    if in_year < 2010 or in_year > 2018:
        raise ValueError("Input parameter {} is out of range.".format(in_year))
    labels = []
    rate_labels = []
    dfs = []
    summary_all = []
    summary_rate = []

    # Local storage (cache) for the raw data so that iteration time is faster.
    shelf = shelve.open("gr_dfs")
   
    # @NOTE: We process data for all the years even though we only return a dataframe
    # for a single year with each function call. 
    for cur_year in range(2010,2019):
        shelf_key = str(cur_year)
        df = pd.DataFrame()

        if shelf_key in shelf:
            df = shelf[shelf_key]
        else:
            df = make_raw_gr_frame(year=cur_year)
            shelf[shelf_key] = df

        yearStr = year_string(cur_year)
        prefix = 'ALL'
        cur_label = prefix + '_COHORT_' + yearStr
        labels += [cur_label]
        cur_rate_label = prefix + '_RATE_' + yearStr
        rate_labels += [cur_rate_label]
        
        # Clean the ALL column
        # Drop rows with ALL column with a . in it
        df.replace('.',np.nan, inplace=True)
        #df.loc[:,:] = df[df[cur_label] != '.']
        # Convert ALL strings to floats
        df.loc[:,cur_label] = pd.to_numeric(df.loc[:,cur_label])
        # Drop rows with ALL columns unreasonably large 
        df.loc[:,:] = df[df[cur_label] < 8000]
        # Drop rows with NAs in ALL column
        df.dropna(axis=0,subset=cur_label,inplace=True)

        # Clean prefixes from ALL_RATE column
        # @NOTE: A rate of 'GE50' might better be approximated by 75 than 50 like this code does.
        for colname in df.columns:
            if colname.startswith('ALL_RATE_'):
                df.loc[:, colname] = df[colname].str.removeprefix('GE')
                df.loc[:, colname] = df[colname].str.removeprefix('LE')
                df.loc[:, colname] = df[colname].str.removeprefix('GT')
                df.loc[:, colname] = df[colname].str.removeprefix('LT')
        
        # Convert ranges in RATE columns to mean 
        # Drop rows with ALL column with a . in it
        df.loc[:, cur_rate_label].replace('PS',np.nan, inplace=True)
        df.loc[:, cur_rate_label] = df[cur_rate_label].map(conv_range_to_float,na_action='ignore')
        df.loc[:,cur_rate_label] = pd.to_numeric(df.loc[:,cur_rate_label])
        df.dropna(axis=0,subset=cur_rate_label,inplace=True)
      
        # @TODO: convert some columns to categorical to save memory

        # Only save the subset of columns that we need.
        dfs.append(df[['NCESSCH','STNAM','LEAID','SCHNAM', \
            'ALL_COHORT_' + year_string(cur_year), 'ALL_RATE_' + year_string(cur_year)]])
    # Shelve teardown
    shelf.close()

    return dfs[in_year-2010]


def verify_ALL_column_clean():
    """ Sum up all the NANs in the ALL column for all the years in the range. 
        Print summary statistics for the ALL column for all years in range.
    """
    totalNas = 0
    for idx, df in enumerate(dfs):
        totalNas += sum(df[labels[idx]].isna())
        print(df[labels[idx]].describe())
    print("Total Nas remaining in ALL columns:", totalNas)

def verify_ALL_RATE_column_clean():
    """ Sum up all the NANs in the ALL_RATE column for all the years in the range. 
        Print summary statistics for the ALL_RATE column for all years in range.
    """
    totalNas = 0
    for idx, df in enumerate(dfs):
        totalNas += sum(df[rate_labels[idx]].isna())
        print(df[rate_labels[idx]].describe())
    print("Total Nas remaining in ALL_RATE columns:", totalNas)

def verify_dtypes():
    for df in dfs:
        print(df.dtypes)


if __name__ == "__main__":
    """ Call debugging / verification functions by uncommenting so you can see summary
    statistics across all the years. """
    #verify_ALL_column_clean()
    #verify_ALL_RATE_column_clean()
    #verify_dtypes()

    

