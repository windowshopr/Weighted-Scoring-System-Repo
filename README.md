INTRODUCTION
This repo contains a script that allows a user to calculate a weighted (by column) "score" for each row in a dataset. A sample dataset is included in the "input_datasets" folder, and a sample output file is in the "output_datasets" folder already.

Using the example provided, we have a dataset of various trading strategy's performance metrics, and we are trying to find what strategy has the "best" results out of all the others.

ENVIRONMENT
Windows 10, Python 3.7.9

REQUIREMENTS
pandas==1.2.5
tqdm==4.64.0

INSTALLATION
Download this repo and unzip the .zip file somewhere useful.

USAGE
1. Load a dataset in .CSV or .XLSX format into the "input_datasets" folder.
2. Run python main.py
3. Inspect the "output_datasets" for the scored table

VARIABLES TO SET


NOTES
1. The program only runs with .CSV and .XLSX files as is, you can add more formats if desired.
2. The program has only been tested with the above mentioned environment, although I'm sure other versions of the dependencies will work too.
3. The program will use every file in the "input_datasets" folder each time it's run. I have a check to warn the user if an output'd dataset already exists for each input file to protect against accidental overwriting, but best practise would be to remove the file from the "input_datasets" folder once it's scored.

# ------------------------------------------------------------------------------------------------ #
#                                          USER VARIABLES                                          #
# ------------------------------------------------------------------------------------------------ #
# Define some minimum cutoffs, or in other words, drop 
# all rows in the datasets where these columns have 
# have values less than their corresponding mimumum value.
# Example: If "Profit" value is 0, keep all rows where
#          "Profit" > 0, drop rows where "Profit" <= 0.
min_cutoffs = {# "Profit": 0,
              }

# Define some maximum cutoffs.
# Example: drop all rows where "Equity DD %" >= 50,
#          keep rows where "Equity DD %" < 50.
max_cutoffs = {#"Equity DD %": 50,
              }

# Columns to score and their weightings (higher number
# = more importance put on that score being better).
score_cols_with_weights = {#"Avg # Bars In Losing Trades: All": 1,
# "Avg # Bars In Winning Trades: All": 1,
# # "Avg Losing Trade: All": 1,
# "Avg Losing Trade %: All": 1,
# # "Avg Trade: All": 1,
# "Avg Trade %: All": 1,
# # "Avg Winning Trade: All": 1,
# "Avg Winning Trade %: All": 1,
# "Commission Paid: All": 1,
# # "Gross Loss: All": 1,
# "Gross Loss %: All": 1,
# # "Gross Profit: All": 1,
# "Gross Profit %: All": 1,
# # "Largest Losing Trade: All": 1,
# "Largest Losing Trade %: All": 1,
# # "Largest Winning Trade: All": 1,
# "Largest Winning Trade %: All": 1,
# # "Net Profit: All": 1,
"Net Profit %: All": 2,
# "Number Losing Trades: All": 1,
# "Number Winning Trades: All": 1,
"Percent Profitable: All": 2,
"Profit Factor: All": 1,
# "Ratio Avg Win / Avg Loss: All": 1,
"Total Closed Trades: All": 2,
# # "Max Drawdown": 1,
# "Open PL": 1,
# "Sharpe Ratio": 1,
# "Sortino Ratio": 1,
"Max Drawdown %": 2,
# "Open PL %": 1,

}

# Which columns do a LOWER score mean it's better?
smaller_col_score_is_better_list = ["Avg # Bars In Losing Trades: All",
# "Avg Losing Trade: All", 
"Avg Losing Trade %: All",
"Commission Paid: All",
# "Gross Loss: All",
"Gross Loss %: All",
# "Largest Losing Trade: All",
"Largest Losing Trade %: All",
"Number Losing Trades: All",
# "Max Drawdown",
"Max Drawdown %",
]#["Equity DD %"]


# If 2 results have the same "CombinedScore", use this
# column as the tiebreaker when sorting the results
tiebreaker_col = "Net Profit %: All"

# Define a list of percentiles to use. This is messy,
# but for visualization purposes, it's fine
quantiles = [0.2,0.4,0.6,0.8]



##########################################################
# Read all files in "input_datasets" folder
##########################################################
# Get a list of all files in "input_datasets" folder
filenames = next(walk("input_datasets/"), (None, None, []))[2]  # [] if no file
print(filenames)

# Iterate through all of them
for filename in filenames:

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
        df.to_excel("output_datasets/" + filename, index=False)
    elif ".csv" in filename:
        df.to_csv("output_datasets/" + filename, index=False)

print("\nDone! Check the 'output_datasets' folder for the resulting")
print("datasets. The 'CombinedScore' column will be on the far right.")