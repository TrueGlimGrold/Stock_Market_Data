import pandas as pd 
import os
import csv
from datetime import datetime, timedelta

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

# Function to analyze patterns
def analyze_patterns(df):
    patterns = {'increase': 0, 'decrease': 0, 'increase_and_lead_to_higher': 0, 'decrease_and_lead_to_higher': 0}

    for i in range(1, len(df)):
        if df['open'][i] > df['open'][i - 1]:
            patterns['increase'] += 1
        elif df['open'][i] < df['open'][i - 1]:
            patterns['decrease'] += 1

    for i in range(len(df) - 252):  # Check one year later
        if df['open'][i + 252] > df['open'][i]:
            patterns['increase_and_lead_to_higher'] += 1
        elif df['open'][i + 252] < df['open'][i]:
            patterns['decrease_and_lead_to_higher'] += 1

    print(f"Analyzed {df['filename'].iloc[0]}")
    return patterns

# Analyze patterns for each file
result_list = []
unique_filenames = data['filename'].unique()

for filename in unique_filenames:
    df = data[data['filename'] == filename].reset_index(drop=True)
    patterns = analyze_patterns(df)
    result_list.append({'filename': filename, **patterns})

# Convert the result list to a DataFrame
result_df = pd.DataFrame(result_list)

# Calculate percentages
result_df['increase_percentage'] = result_df['increase_and_lead_to_higher'] / result_df['increase'] * 100
result_df['decrease_percentage'] = result_df['decrease_and_lead_to_higher'] / result_df['decrease'] * 100

# Sort by decrease_percentage in descending order
result_df = result_df.sort_values(by='decrease_percentage', ascending=False)

# Print the result DataFrame
print(result_df)