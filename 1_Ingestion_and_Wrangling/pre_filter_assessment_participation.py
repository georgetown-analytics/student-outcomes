import os
import sys
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


# Note that this can be changed to ingest from S3. The data is in the WORM store
dataset_dir = "/home/bb/datasets/state_test_participation/"

math_files = []
rla_files = []
for root, dirs, files in os.walk(dataset_dir, topdown=False):
    for f in files:
        if f.startswith("math"):
            math_files += [f]
        if f.startswith("rla"):
            rla_files += [f]
        print(f)
# We have 7 years of percent participated scores for math and the same 7 for reading & language arts
len(math_files), len(rla_files)

# Create raw math and rla dataframe lists
math_dfs = [pd.read_csv(dataset_dir + "/" + i, low_memory=False)
            for i in math_files]
rla_dfs = [pd.read_csv(dataset_dir + "/" + i, low_memory=False)
           for i in rla_files]


# Inspecting the codebook, we see that there are only two columns relevant to our study.
# These are the percentage participation numbers in math and reading / language arts state assessments.
# Extract the total participation column names that are relevant to high schools
list(map(lambda x: print(x.filter(like="ALL_MTHHSPCT").columns), math_dfs))
list(map(lambda x: print(x.filter(like="ALL_RLAHSPCT").columns), rla_dfs))
list(map(lambda x: print(x.filter(like="NCESSCH").columns), math_dfs))
list(map(lambda x: print(x.filter(like="NCESSCH").columns), rla_dfs))


### Strategy:
"""
* Subset the dataframes to our columns of interest e.g. (NCESSCH, ALL_MTHHSPCTPART_1213, ALL_RLAHSPCTPART_1213)
* Create one large math and one large language arts dataframe with all the years stacked, so that it matches our graduation rate and school directory dataframes
* Merge and save these to disk 
"""

def year_string(y: int):
    """Input an integer year and get a range that matches the column suffixes in the raw data.
    e.g. 2011 => 1112 and 2018 => 1819."""
    return str(y)[-2:] + str(int(str(y)[-2:]) + 1)


# Produce large dataframes joined by year

new_math_dfs = []
new_rla_dfs = []

for df in math_dfs:
    pct_part = df.loc[:, [
        'ALL_MTHHSPCT' in i or 'ALL_MTHHSpct' in i for i in df.columns]]
    unaltered_year = pct_part.columns[0][-4:]
    year = int("20" + pct_part.columns[0][-4:-2])
    year_df = pd.DataFrame()
    year_df['Year'] = np.array([year] * len(pct_part))
    ncessch = df.filter(like='NCESSCH')
    pct_part.rename(mapper={"ALL_MTHHSPCTPART_" +
                    unaltered_year: "Math_Pct_Part"}, axis=1, inplace=True)
    pct_part.rename(mapper={"ALL_MTHHSpctpart_" +
                    unaltered_year: "Math_Pct_Part"}, axis=1, inplace=True)
    assert isinstance(pct_part, pd.DataFrame)
    assert isinstance(year_df, pd.DataFrame)
    assert isinstance(ncessch, pd.DataFrame)
    assert len(pct_part) == len(year_df) == len(ncessch)
    new_df = pd.concat([year_df, ncessch, pct_part], axis=1)
    new_math_dfs += [new_df]


for df in rla_dfs:
    pct_part = df.loc[:, [
        'ALL_RLAHSPCT' in i or 'ALL_RLAHSpct' in i for i in df.columns]]
    unaltered_year = pct_part.columns[0][-4:]
    year = int("20" + pct_part.columns[0][-4:-2])
    year_df = pd.DataFrame()
    year_df['Year'] = np.array([year] * len(pct_part))
    ncessch = df.filter(like='NCESSCH')
    pct_part.rename(mapper={"ALL_RLAHSPCTPART_" +
                    unaltered_year: "Rla_Pct_Part"}, axis=1, inplace=True)
    pct_part.rename(mapper={"ALL_RLAHSpctpart_" +
                    unaltered_year: "Rla_Pct_Part"}, axis=1, inplace=True)
    assert isinstance(pct_part, pd.DataFrame)
    assert isinstance(year_df, pd.DataFrame)
    assert isinstance(ncessch, pd.DataFrame)
    assert len(pct_part) == len(year_df) == len(ncessch)
    new_df = pd.concat([year_df, ncessch, pct_part], axis=1)
    new_rla_dfs += [new_df]


big_math_df = pd.concat(new_math_dfs, axis=0)
big_rla_df = pd.concat(new_rla_dfs, axis=0)

# Merge RLA and PCT prof on 'Year' and 'Ncessch"
merged_data = big_math_df.merge(big_rla_df, how='left', on=["Year", "NCESSCH"])
merged_data.dropna(inplace=True)
merged_data.to_csv('../notebooks/math_rla_percent_participation_prefiltered.csv.bak',index=False)
