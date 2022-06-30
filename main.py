# ------------------------------------------------------------------------------------------------ #
#                                              IMPORTS                                             #
# ------------------------------------------------------------------------------------------------ #
import pandas as pd 
from os import walk, path
from tqdm import tqdm

# ------------------------------------------------------------------------------------------------ #
#                                          USER VARIABLES                                          #
# ------------------------------------------------------------------------------------------------ #
# Define some minimum cutoffs, or in other words, drop 
# all rows in the datasets where these columns have 
# have values less than their corresponding mimumum value.
# Example: If "Profit Factor" value is 1, keep all rows where
#          "Profit Factor" > 1, drop rows where "Profit Factor" <= 1.
min_cutoffs = {"Profit Factor": 1, }

# Define some maximum cutoffs.
# Example: drop all rows where "Num of Trades" >= 5000,
#          keep rows where "Num of Trades" < 5000.
max_cutoffs = {"Num of Trades": 100, }

# Columns to score and their weightings (higher number
# = more importance put on that score being better).
score_cols_with_weights = {"P:L Ratio": 1,
                           "Profit Factor": 1,
                           "Win Rate %": 1,
                           "Max Drawdown %": 1,
                           "Est. Avg Drawdown %": 1,
                           "Num of Trades": 1,
                           "Average Trade %": 1,
                           "Best Trade %": 1,
                           "Worst Trade %": 1,
                           "Final Comp Equity": 1,
}

# Which columns do a LOWER score mean it's better?
# These would be columns with numbers that you want to see go down, not up.
# Drawdown would be a good example of this, however because drawdowns in the
# example document are already negative, we want them to go UP (closer to 0),
# So they are NOT included in this list below.
smaller_col_score_is_better_list = [#"Avg # Bars In Losing Trades: All", 
                                    ]

# If 2 results have the same "CombinedScore" in the end, use this
# column as the tiebreaker when sorting the results
tiebreaker_col = "Profit Factor"

# Define a list of percentiles to use. Example, [0.2,0.4,0.6,0.8].
# If a metric falls below the 0.2 quantile in its respective column,
# if gets 1 weight point as defined in score_cols_with_weights. If
# it's between 0.6 and 0.79, it would get 4 points.
quantiles = [0.25, 0.5, 0.75]



# ------------------------------------------------------------------------------------------------ #
#                            READ ALL FILES IN THE INPUT_DATASETS FOLDER                           #
# ------------------------------------------------------------------------------------------------ #
# Get a list of all files in "input_datasets" folder
filenames = next(walk("input_datasets/"), (None, None, []))[2]  # [] if no file
print(filenames)

# Iterate through all of them
for filename in filenames:
    
    # Check if there's an output dataset already for the current file
    if path.exists("output_datasets/output_" + filename):
        answer = input("WARNING - there's already a score dataset for the file " + str(filename) + ". Do you want to run this script and overwrite that output file? (Y or N or Q to quit): ")
        early_quit = False
        if answer.lower() in ['n', 'no']:
            continue
        elif answer.lower() in ['q', 'quit', 'exit']:
            early_quit = True
            break
    # Is it a .csv or a .xlsx format? Else, just skip the file
    if ".xlsx" in filename or ".xlsm" in filename:
        df = pd.read_excel("input_datasets/" + filename)
    elif ".csv" in filename:
        df = pd.read_csv("input_datasets/" + filename)
    else:
        continue
    
    # Inspect the original dataframe
    print(df)

    # If "min_cutoffs" have been defined above, trim the
    # rows we don't want now
    if len(min_cutoffs):
        for key, value in min_cutoffs.items():
            df = df[(df[key] > value)]

    # If "max_cutoffs" have been defined above, trim the
    # rows we don't want now
    if len(max_cutoffs):
        for key, value in max_cutoffs.items():
            df = df[(df[key] < value)]

    # Make an empty CombinedScore column
    df['CombinedScore'] = 0

    # Create a "quantiles_df". NOTE, if you get a NameError, it's
    # likely becuase that column isn't all numeric values, i.e.
    # there's "NaN" or a string in it somewhere. Fix that so that
    # the entire column is numeric before continuing.
    quantiles_df = df.quantile(quantiles)

    print("CALCULATING COMBINED SCORES......")

    # Start a progress bar and iterate through each row of the df
    # (after we've done the cutoff row dropping above to save time)
    for i in tqdm(range(len(df))):

        # Loop through all the quantiles
        for quantile in quantiles:

            # ...and through all the columns we want to score
            for key, value in score_cols_with_weights.items():

                # First, check if it's one of the columns where a 
                # LOWER score should be graded higher
                if key in smaller_col_score_is_better_list:

                    # For every percentile better the current value is 
                    # compared to the column it's in, add the weight to
                    # it's current score (weights for the columns defined
                    # above already)
                    if df[key].iloc[i] <= quantiles_df.at[quantile, key]:
                        df['CombinedScore'].iloc[i] += value
                    # Continue here
                    continue

                # Otherwise, if it's a metric where a HIGHER number should
                # receive more points, do it this way (hence the continue
                # above)
                if df[key].iloc[i] >= quantiles_df.at[quantile, key]:
                    df['CombinedScore'].iloc[i] += value

    # Sort the final df by "CombinedScore" metric, then by "tiebreaker_col" 
    # as a tie breaker
    df = df.sort_values(['CombinedScore', tiebreaker_col], ascending=[False, False])
    
    # Inspect the final df
    print(df)

    # Save the final df in the same format as it was imported
    if ".xlsx" in filename:
        df.to_excel("output_datasets/output_" + filename, index=False)
    elif ".csv" in filename:
        df.to_csv("output_datasets/output_" + filename, index=False)

# Give a final message, depending on what user selected for quitting.
if not early_quit:
    print("\nDone! Check the 'output_datasets' folder for the resulting")
    print("datasets. The 'CombinedScore' column will be on the far right.")
elif early_quit:
    print("\Early quitting! Check the 'output_datasets' folder for any resulting")
    print("datasets created before quitting. The 'CombinedScore' column will be on the far right.")