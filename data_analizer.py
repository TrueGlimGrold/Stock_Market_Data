import pandas as pd 
import os
import csv
from datetime import datetime, timedelta
import sys
import progressbar 

# Path to the "Stocks" folder
stocks_folder = "archive/Stocks"

# Lists to store data
filename_list = []
date_list = []
open_list = []
high_list = []
low_list = []
close_list = []
volume_list = []
open_int_list = []

# Loop through each file in the "Stocks" folder
for filename in os.listdir(stocks_folder):
    if filename.endswith(".txt"):
        file_path = os.path.join(stocks_folder, filename)
        
        # Open and read the CSV file
        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file)
            
            try:
                # Skip the header row
                header = next(csv_reader)
            except StopIteration:
                print(f"Warning: Empty file - {filename}")
                continue
            
            # Iterate through each row and extract data
            for row in csv_reader:
                filename_list.append(filename)
                date_list.append(row[0])
                open_list.append(row[1])
                high_list.append(row[2])
                low_list.append(row[3])
                close_list.append(row[4])
                volume_list.append(row[5])
                open_int_list.append(row[6])
                
titled_columns = {"filename": filename_list,
                 "date": date_list,
                 "open": open_list,
                 "high": high_list,
                 "low": low_list,
                 "volume": volume_list,
                 "openInt": open_int_list}
                

# Start using the data
data = pd.DataFrame(titled_columns)

unique_filenames = data['filename'].unique()

# List to store results for each file
all_results = []

def clear_line(): 
    sys.stdout.write('\033[F')  # Move the cursor up one line
    sys.stdout.write('\033[K')  # Clear the line

def analize_streaks(df):
    patterns = {'increase_streak': 0, 'decrease_streak': 0, 'lead_to_higher': True}

    # Variables to track streaks
    increase_streak = 0
    decrease_streak = 0

    for i in range(1, len(df)):
        if df['open'][i] > df['open'][i - 1]:
            increase_streak += 1
            decrease_streak = 0
        elif df['open'][i] < df['open'][i - 1]:
            decrease_streak += 1
            increase_streak = 0
        else:
            increase_streak = 0
            decrease_streak = 0

    # Check one year later
    try:
        if df['open'][252] > df['open'][0]:
            patterns['lead_to_higher'] = False
    except: 
        pass

    # Update patterns dictionary
    patterns['increase_streak'] = increase_streak
    patterns['decrease_streak'] = decrease_streak

    # print(f"Analyzed {df['filename'].iloc[0]}")
    return patterns

# Create a progress bar for file processing
widgets_files = [progressbar.Percentage(), ' ', progressbar.Counter(), ' ',
                    progressbar.Bar(), ' ', progressbar.Timer(), ' ']
progress_bar_files = progressbar.ProgressBar(widgets=widgets_files, maxval=len(unique_filenames)).start()

# ! First analysis of data

for idx, filename in enumerate(data['filename'].unique()):
    df = data[data['filename'] == filename].reset_index(drop=True)

    # Skip empty files
    if df.empty:
        continue

    # Update progress bar for file processing
    progress_bar_files.update(idx + 1)

# Finish the progress bar
progress_bar_files.finish()

# Sort the DataFrame by 'open' column in descending order
sorted_data = data.sort_values(by='open', ascending=False)

# Display the sorted results
print(sorted_data[['filename', 'date', 'open']].head(30))


# ! Second analysis of data

# Define percentiles for categorization
percentiles = [0, 1, 10, 30, 50, 70, 90, 99, 100]

# Scale percentiles to be in the range [0, 1]
scaled_percentiles = [p / 100 for p in percentiles]

# Replace non-numeric values in the 'open' column with NaN
data['open'] = pd.to_numeric(data['open'], errors='coerce')

# Define percentiles for categorization
percentiles = [0, 1, 10, 30, 50, 70, 90, 99, 100]

# Scale percentiles to be in the range [0, 1]
scaled_percentiles = [p / 100 for p in percentiles]

# Replace non-numeric values in the 'open' column with NaN
data['open'] = pd.to_numeric(data['open'], errors='coerce')

# Check if there are any non-numeric values in the 'open' column
if data['open'].notna().all():
    # Check if there are enough non-NaN values to perform the calculation
    if len(data['open'].dropna()) > 1:
        # Calculate percentage increase only if there are enough non-NaN values
        data['percentage_increase'] = (data['open'].shift(-252) - data['open']) / (data['open'] + 1e-8) * 100

        # Drop NaN values from the 'percentage_increase' column
        data['percentage_increase'].dropna(inplace=True)

        # Check if there are enough non-NaN values to perform quantile calculation
        if len(data['percentage_increase']) > 1:
            # Calculate quantiles
            quantiles = data['percentage_increase'].quantile(q=scaled_percentiles, interpolation='linear')

            # Remove duplicate quantile values
            quantiles = quantiles[~quantiles.duplicated()]

            # Ensure there are enough unique quantiles
            if len(quantiles) < len(scaled_percentiles) - 1:
                print("Not enough unique quantiles.")
            else:
                # Categorize stocks based on reversed percentiles for all files
                data['percentile_category'] = pd.cut(
                    data['percentage_increase'],
                    bins=quantiles,
                    labels=[
                        f'Top {100 - p*100}%' if p > 0 else f'Bottom {-p*100}%'
                        for p in scaled_percentiles[:-1]
                    ]
                )

                # Group by percentile category and calculate average percentage increase
                result = data.groupby('percentile_category', observed=False)['percentage_increase'].mean()

                # Print the combined result
                print("Average Result:")
                for category, value in zip(result.index, result):
                    print(f"{category}: {value}")
                    
                # Group by percentile category and calculate median percentage increase
                result = data.groupby('percentile_category', observed=False)['percentage_increase'].median()

                # Print the combined result
                print("Median Result:")
                for category, value in zip(result.index, result):
                    print(f"{category}: {value}")
        else:
            print("Not enough non-NaN values for percentage increase.")
    else:
        print("Not enough non-NaN values for 'open' column.")
else:
    print("Some non-numeric values in the 'open' column.")
    
# ! Third analysis of data. 

# Initialize result arrays
increase_result_array = {}
increase_full_size_array = {}
decrease_result_array = {}
decrease_full_size_array = {}

# Initialize result arrays
increase_result_array = {}
increase_full_size_array = {}
decrease_result_array = {}
decrease_full_size_array = {}

for idx, filename in enumerate(unique_filenames):
    df = data[data['filename'] == filename].reset_index(drop=True)
    patterns = analize_streaks(df)

    # Initialize result arrays for the streak length if not already done
    if patterns['increase_streak'] not in increase_result_array:
        increase_result_array[patterns['increase_streak']] = 0
        increase_full_size_array[patterns['increase_streak']] = 0

    if patterns['decrease_streak'] not in decrease_result_array:
        decrease_result_array[patterns['decrease_streak']] = 0
        decrease_full_size_array[patterns['decrease_streak']] = 0

    # Update result arrays for increase streaks
    if patterns['increase_streak'] > 0 and patterns['lead_to_higher']:
        increase_result_array[patterns['increase_streak']] += 1
        increase_full_size_array[patterns['increase_streak']] += 1
    else:
        increase_full_size_array[patterns['increase_streak']] += 1

    # Update result arrays for decrease streaks
    if patterns['decrease_streak'] > 0 and not patterns['lead_to_higher']:
        decrease_result_array[patterns['decrease_streak']] += 1
        decrease_full_size_array[patterns['decrease_streak']] += 1
    else:
        decrease_full_size_array[patterns['decrease_streak']] += 1
        
    clear_line()

    # Clear the last line before updating progress bar for file processing
    progress_bar_files.update(idx)


# Finish the progress bar for file processing
progress_bar_files.finish()

# Analyze results for increase streaks
for streak_length in increase_full_size_array:
    if increase_result_array[streak_length] > 0:
        success_rate = increase_result_array[streak_length] / increase_full_size_array[streak_length]
        print(f"Increase Streak: {streak_length}, Success Rate: {success_rate * 100:.2F}%")
    else:
        print(f"Increase Streak: {streak_length}, No successful outcomes")

# Analyze results for decrease streaks
for streak_length in decrease_full_size_array:
    if decrease_result_array[streak_length] > 0:
        success_rate = decrease_result_array[streak_length] / decrease_full_size_array[streak_length]
        print(f"Decrease Streak: {streak_length}, Success Rate: {success_rate * 100:.2F}%")
    else:
        print(f"Decrease Streak: {streak_length}, No successful outcomes")
        
