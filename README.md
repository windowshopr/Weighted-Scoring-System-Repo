# DISCLAIMER
All of my repositories (including this one) are NOT actively maintained. I have disabled issues, so if you decide to download or use any of my projects, you will troubleshoot any issues yourself. You can safely assume that most of my repo's are in a "proof-of-concept" stage; some of them are completed and working, others are just templates that need more work. The repo's I choose to post on GitHub are meant for review, storage and job applications. Any use or misuse of my projects from others are done without my consent and I accept no responsibility for their actions. Thank you.


# INTRODUCTION
This repo contains a script that allows a user to calculate a weighted (by column) "score" for each row in a dataset. A sample dataset is included in the "input_datasets" folder, and a sample output file is in the "output_datasets" folder already. I invite you to read the example run through and variable definitions below as most of your questions will be answered there already.


# ENVIRONMENT
- Windows 10
- Python 3.7.9


# REQUIREMENTS
- pandas==1.2.5
- tqdm==4.64.0


# INSTALLATION
Download this repo and unzip the .zip file somewhere useful.

# USAGE
1. Load a dataset in .CSV or .XLSX format into the "input_datasets" folder
2. Define the variables in main.py (described below)
2. Run python main.py
3. Inspect the "output_datasets" for the scored table


## HIGH LEVEL OVERVIEW AND EXAMPLE RUN
Using the example provided, we have a dataset of various trading strategy's performance metrics, and we are trying to find what strategy has the "best" results out of all the others, based on these various metrics. Some have higher Profit than others, some have lower Drawdown than others, some place more trades than others, so how do we determine which is the best overall strategy when considering all of these different metrics?

The script makes use of 2 simple concepts:
1. Weights
2. Quantiles
The **weights** are numbers used to assign "importance" to each column. The higher a column's weight, the more important that column is, and the more "points" it receives when comparing to what "quantile" the current value falls into.

The **quantiles** are used to determine how many weighted "points" are given to each column, based on the current row's value compared to all the other values in the same column.

Example: Let's assume that every column in the provided dataset are equally important when compared to one another. Our "score_cols_with_weights" dictionary would look like this:

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

These are all the columns (apart from the "Strategy" column as it is non-numeric) that we want to consider in the final combined score. Notice the 1's used for every column. If we felt like, for example, the "Profit Factor" and "Max Drawdown %" were more "important" than all of the others, we could assign a weight of 2 or more to those columns, making sure those are weighted higher. But to keep it simple, let's assume they're all equally important.

Now, we can assign a quantiles list. Let's assume our quantiles are:

quantiles = [0.25, 0.5, 0.75]

Good. So now when the program starts, it'll iterate through each column, determine each of the quantile values for that column, then iterate through each row. Depending on the current value as compared to the quantile values, that will determine what "score" that row's value receives.

Example: quantile values of "Profit Factor" column = [0.5, 1, 1.5]
if current row's "Profit Factor" <= 0.5, add 1 weight point. If it's <= 1, add another weighted point. If it's <= 1.5, add another weighted point. If it's > 1.5, add another weighted point.
So if the current row's Profit Factor is 2.0, it would receive 4 x 1 weight point = 4 points.
If the next row's Profit Factor is 0.75, it would receive 2 x 1 weight points = 2 points.

NOTE: If the Profit Factor had a 2 weight instead of a 1 weight as defined in "score_cols_with_weights", these two would receive 4 x 2 weight points = 8 points, and 2 x 2 weight points = 4 points respectively.

It repeats this process for each column in the dataset, giving a combined sum of all weight points in the end, and sorts by the highest combined score. You can view your weighted results (and see the "best" row) in the "output_datasets" folder.

The "quantiles" and "weights" are hyperparameters that you will need to tune, based on trial and error/intuition into the problem, so experiment with different weights, and quantile values (like quantiles = [0.2, 0.4, 0.6, 0.8] and different weight numbers in "score_cols_with_weights").


# VARIABLES TO SET
## min_cutoffs
Define some minimum cutoffs, or in other words, drop all rows in the datasets where values are less than their corresponding mimumum before performing the scoring run. Example: If minimum "Profit Factor" value is 1, keep all rows where "Profit Factor" > 1, drop rows where "Profit Factor" <= 1. This helps to remove outliers, and shrink the search space before performing the scoring run. Dictionary format. If you don't want to define any cutoffs, leave this as an empty dictionary with no keys or values in it.
min_cutoffs = {"Profit Factor": 1, }

## max_cutoffs
Define some maximum cutoffs. Example: drop all rows where "Num of Trades" >= 100, keep rows where "Num of Trades" < 100. Dictionary format. If you don't want to define any cutoffs, leave this as an empty dictionary with no keys or values in it.
max_cutoffs = {"Num of Trades": 100, }

## score_cols_with_weights
Columns to score and their weightings (higher number = more importance put on that score being better). Dictionary format.
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

## smaller_col_score_is_better_list
Which columns do a LOWER score mean it's better? These would be columns with numbers that you want to see go down, not up. Drawdown would be a good example of this, however, because drawdowns in the example document are already represented as negative numbers, technically we want them to go UP (closer to 0), so they are NOT included in this list below. List format. If you don't have any columns that where the values should decrease, leave this as an empty list with no values in it.
smaller_col_score_is_better_list = [#"Avg # Bars In Losing Trades: All", 
                                    ]

## tiebreaker_col
If 2 results have the same "CombinedScore" in the end, use this column as the tiebreaker when sorting the results at the end. String (Column name).
tiebreaker_col = "Profit Factor"

## quantiles
Define a list of percentiles to use. Example, [0.2,0.4,0.6,0.8]. If a metric falls below the 0.2 quantile value in its respective column, if gets 1 weight point as defined in score_cols_with_weights. If it's between 0.6 and 0.79, it would get 4 points. List format or floats between 0 and 1.
quantiles = [0.25, 0.5, 0.75]


# FINAL NOTES
1. The program only runs with .CSV and .XLSX files as is, you can add more formats if desired.
2. The program has only been tested with the above mentioned environment, although I'm sure other versions of the dependencies will work too.
3. The program will use every file in the "input_datasets" folder each time it's run. I have a check to warn the user if an output'd dataset already exists for each input file to protect against accidental overwriting, but best practise would be to remove the file from the "input_datasets" folder once it's scored.
4. If you get a "NameError", it's likely because you have inf's, nan's, or a non-numeric value somewhere in your dataset. Make sure every value in the columns you define in your "score_cols_with_weights" variable are numeric only.
