import pandas as pd 
import os
import csv
from datetime import datetime, timedelta
import sys
import progressbar 

os.system('cls')

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

# Function to clear the last line in the console
def clear_last_line():
    sys.stdout.write('\033[F')  # Move the cursor up one line
    sys.stdout.write('\033[K')  # Clear the line

def analyze_patterns(df):
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
    except: print(" --- No data within a year ---")

    # Update patterns dictionary
    patterns['increase_streak'] = increase_streak
    patterns['decrease_streak'] = decrease_streak

    # print(f"Analyzed {df['filename'].iloc[0]}")
    return patterns

unique_filenames = data['filename'].unique()

# Initialize result arrays
increase_result_array = {}
increase_full_size_array = {}
decrease_result_array = {}
decrease_full_size_array = {}

# Create a progress bar for file processing
widgets_files = [progressbar.Percentage(), ' ', progressbar.Counter(), ' ',
                    progressbar.Bar(), ' ', progressbar.Timer(), ' ']
progress_bar_files = progressbar.ProgressBar(widgets=widgets_files, maxval=len(unique_filenames)).start()

# Initialize result arrays
increase_result_array = {}
increase_full_size_array = {}
decrease_result_array = {}
decrease_full_size_array = {}

for idx, filename in enumerate(unique_filenames):
    df = data[data['filename'] == filename].reset_index(drop=True)
    patterns = analyze_patterns(df)

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

    # Clear the last line before updating progress bar for file processing
    clear_last_line()
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