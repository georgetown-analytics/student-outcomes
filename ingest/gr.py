import sys, os

sys.path.append(os.getcwd() + "/..")
import pandas as pd
import numpy as np
import shelve

urls = (
    "https://www2.ed.gov/about/inits/ed/edfacts/data-files/acgr-sch-sy2010-11.csv",
    "https://www2.ed.gov/about/inits/ed/edfacts/data-files/acgr-sch-sy2011-12.csv",
    "https://www2.ed.gov/about/inits/ed/edfacts/data-files/acgr-sch-sy2012-13.csv",
    "https://www2.ed.gov/about/inits/ed/edfacts/data-files/acgr-sch-sy2013-14.csv",
    "https://www2.ed.gov/about/inits/ed/edfacts/data-files/acgr-release2-sch-sy2014-15.csv",
    "https://www2.ed.gov/about/inits/ed/edfacts/data-files/acgr-sch-sy2015-16.csv",
    "https://www2.ed.gov/about/inits/ed/edfacts/data-files/acgr-sch-sy2016-17.csv",
    "https://www2.ed.gov/about/inits/ed/edfacts/data-files/acgr-sch-sy2017-18.csv",
    "https://www2.ed.gov/about/inits/ed/edfacts/data-files/acgr-sch-sy2018-19-wide.csv",
)


common_core_of_data_url = (
    "https://educationdata.urban.org/csv/ccd/schools_ccd_directory.csv"
)


def make_raw_gr_frame(year):
    """Create raw graduation rate dataframe for a given year directly from the .csv url. It is 'raw' because
    no modifications are done and it is cached locally as-is."""
    # Verify input parameter is valid
    if year not in list(range(2010, 2019)):
        raise ValueError("input parameter {} is out of range.".format(year))

    # Local storage (cache) for the raw data so that iteration time is faster.
    shelf = shelve.open("gr_dfs")

    df = pd.DataFrame()
    shelf_key = str(year)

    if shelf_key in shelf:
        df = shelf[shelf_key]
    else:
        df = pd.read_csv(urls[year - 2010])
        shelf[shelf_key] = df

    # Shelve teardown
    shelf.close()
    return df


def conv_range_to_float(t: str):
    """Take in a numeric range given as a string, e.g. "10-20" and return the midpoint as a float."""
    vals = t.split("-")
    if len(vals) == 2:
        val1, val2 = float(vals[0]), float(vals[1])
        return val1 / 2.0 + val2 / 2.0
    else:
        return t


def year_string(y: int):
    """Input an integer year and get a range that matches the column suffixes in the raw data.
    e.g. 2011 => 1112 and 2018 => 1819."""
    return str(y)[-2:] + str(int(str(y)[-2:]) + 1)


def make_clean_grad_rate_frame(in_year):
    """Takes in a valid year. Returns a dataframe with identifiers for the school,
    the size of the cohort, and the graduation rate.
    + Trim prefixes
    + Replace ranges with average
    + Replace PS with NaN
    + Convert to numeric
    + Drop NaNs
    """
    if in_year < 2010 or in_year > 2018:
        raise ValueError("Input parameter {} is out of range.".format(in_year))
    labels = []
    rate_labels = []
    dfs = []
    summary_all = []
    summary_rate = []

    # @NOTE: We process data for all the years even though we only return a dataframe
    # for a single year with each function call.
    for cur_year in range(2010, 2019):
        df = pd.DataFrame()

        df = make_raw_gr_frame(year=cur_year)

        yearStr = year_string(cur_year)
        prefix = "ALL"
        cur_label = prefix + "_COHORT_" + yearStr
        labels += [cur_label]
        cur_rate_label = prefix + "_RATE_" + yearStr
        rate_labels += [cur_rate_label]

        # Clean the ALL column
        # Drop rows with ALL column with a . in it
        df.replace(".", np.nan, inplace=True)
        # df.loc[:,:] = df[df[cur_label] != '.']
        # Convert ALL strings to floats
        df.loc[:, cur_label] = pd.to_numeric(df.loc[:, cur_label])
        # Drop rows with ALL columns unreasonably large
        df.loc[:, :] = df[df[cur_label] < 8000]
        # Drop rows with NAs in ALL column
        df.dropna(axis=0, subset=cur_label, inplace=True)

        # Clean prefixes from ALL_RATE column
        # @NOTE: A rate of 'GE50' might better be approximated by 75 than 50 like this code does.
        for colname in df.columns:
            if colname.startswith("ALL_RATE_"):
                df.loc[:, colname] = df[colname].str.removeprefix("GE")
                df.loc[:, colname] = df[colname].str.removeprefix("LE")
                df.loc[:, colname] = df[colname].str.removeprefix("GT")
                df.loc[:, colname] = df[colname].str.removeprefix("LT")

        # Convert ranges in RATE columns to mean
        # Drop rows with ALL column with a . in it
        df.loc[:, cur_rate_label].replace("PS", np.nan, inplace=True)
        df.loc[:, cur_rate_label] = df[cur_rate_label].map(
            conv_range_to_float, na_action="ignore"
        )
        df.loc[:, cur_rate_label] = pd.to_numeric(df.loc[:, cur_rate_label])
        df.dropna(axis=0, subset=cur_rate_label, inplace=True)

        # Only save the subset of columns that we need.
        dfs.append(
            df[
                [
                    "NCESSCH",
                    "STNAM",
                    "LEAID",
                    "SCHNAM",
                    "ALL_COHORT_" + year_string(cur_year),
                    "ALL_RATE_" + year_string(cur_year),
                ]
            ]
        )

    return dfs[in_year - 2010]


def download_raw_common_core_of_data_csv(save_location):
    """Download school directory data from the internet to a specified local save_location. It is an ~900MB CSV file.
    Do not save this to a git repository that is actively being developed. It will break your git push command."""
    try:
        if not os.path.isdir(save_location):
            raise ValueError("save_location must be a valid directory")
        output_path = os.path.join(
            save_location, "common_core_directory_1986_2020_csv.dat"
        )
        print("File will be saved to", output_path)
        print("Starting read operation...")
        df = pd.read_csv(common_core_of_data_url, low_memory=False)
        df.to_csv(output_path)
        print("Operation completed successfully")
    except:
        print("Exception occured while downloading. Try again.")


def make_raw_directory_frame(file_loc="~/datasets/schools_ccd_directory.csv"):
    """Trim down 1986-2020 common core of data file to our years of interest."""
    if not os.path.exists(file_loc):
        raise ValueError("File name given by file_loc does not exist")
    df = pd.read_csv(file_loc, low_memory=False)
    df1 = df[df.year > 2009]
    df2 = df1[df1.year < 2019]
    return df2


def make_clean_school_directory_frame(df_raw):
    """Clean data for columns of interest, dropping schools with NA's in the interesting columns.
    @NOTE: The amount of rows remaining after this function is called is inversely related to the
    number of columns we keep. We can likely remove some columns that do not play an important role in the
    model to keep more data.
    """
    df = df_raw.copy()
    # Select only high schools
    df1 = df[df.highest_grade_offered == 12]
    df2 = df[df.highest_grade_offered == 13]
    df = pd.concat([df1, df2])
    # Select only open schools
    df = df[df.school_status == 1]
    cols_to_keep = [
        "ncessch",
        "year",
        "school_name",
        "zip_location",
        "enrollment",
        "urban_centric_locale",
        "school_type",
        "teachers_fte",
        "title_i_status",
        "charter",
        "magnet",
        "free_or_reduced_price_lunch",
    ]
    df.dropna(subset=["ncessch", "year", "school_name", "zip_location"], inplace=True)
    # Drop other columns
    df = df[cols_to_keep]
    # Cleaning the data so that only schools with a school type are included
    df = df[df.school_type >= 1]
    df.dropna(subset=["school_type"], inplace=True)
    # Cleaning the data so that only schools with a valid number of teachers are included
    df = df[df.teachers_fte >= 1]
    df.dropna(subset=["teachers_fte"], inplace=True)
    # Cleaning the data so that only schools with a valid answer to whether they are virtual
    # df = df[df.virtual >= 0]
    # df.dropna(subset=["virtual"], inplace=True)
    # Cleaning the data so that only schools with provided title I statuses are included
    df = df[df.title_i_status >= 1]
    df.dropna(subset=["title_i_status"], inplace=True)
    # Cleaning the data so that only schools with a provided charter status are included
    df = df[df.charter >= 0]
    df.dropna(subset=["charter"], inplace=True)
    # Cleaning the data so that only schools with a provided magnet status are included
    df = df[df.magnet >= 0]
    df.dropna(subset=["magnet"], inplace=True)
    # Cleaning the data so that only schools with valid reduced lunch information are include
    df = df[df.free_or_reduced_price_lunch >= 0]
    df.dropna(subset=["free_or_reduced_price_lunch"], inplace=True)
    # Cleaning the data so that only schools with valid enrollment count are included
    df = df[df.enrollment >= 0]
    df.dropna(subset=["enrollment"], inplace=True)

    # Instances     Cleaning Statements             Instances Lost
    # 234019        none
    # 234019        school_type                     none
    # 206500        teachers_fte                    medium
    # 124112        virtual                         high
    # 220441        title_i_status                  low
    # 213346        charter                         low
    # 180589        magnet                          medium-high
    # 213717        free_or_reduced_price_lunch     low
    # 229522        enrollment                      low
    return df


if __name__ == "__main__":
    pass
