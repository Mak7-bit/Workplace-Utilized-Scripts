import os
import pandas as pd
import zipfile
import io


def filter_by_contracts(df, contracts):
    df['CONTRACT'] = df['CONTRACT'].str.split(" ").str[1]
    return df[df['CONTRACT'].isin(contracts)]


def save_to_excel(df, file_path):
    if not file_path.endswith('.xlsx'):
        file_path += '.xlsx'
    df.to_excel(file_path, index=False)
    print(f"DataFrame saved as Excel file at {os.path.abspath(file_path)}")

def clean_pick_id(df):
    df['PICK_ID'] = df['PICK_ID'].str.split(" ").str[1]
    return df


# Define the folder path
folder_path = "C:\\Users\\mdmitriev\\OneDrive - Osmose Utilities Services\\Documents\\Python Projects\\scripts\\Automation\\Western Power\\Trial"

# Define contracts
contracts = ['C46972', 'C46607']

# Initialize an empty list to store the data frames
data_frames = []
filtered_and_sorted_data_frames = []

# Traverse through every file and subfolder in the directory
for root, dirs, files in os.walk(folder_path):
    for file in files:
        print(file)
        # Check if the file is a CSV file
        if file.endswith(".csv"):
            # Construct the file path
            file_path = os.path.join(root, file)
            # Read the CSV file into a data frame
            df = pd.read_csv(file_path, encoding='unicode_escape', low_memory=False)
            data_frames.append(df)
            df = filter_by_contracts(df, contracts)
            # Append the data frame to the list of data frames
            filtered_and_sorted_data_frames.append(df)
        # Check if the file is a ZIP file
        elif file.endswith(".zip"):
            # Construct the file path
            file_path = os.path.join(root, file)
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                csv_files = [f for f in zip_file.namelist() if f.endswith('.csv')]
                if len(csv_files) > 0:
                    with zip_file.open(csv_files[0]) as csv_file:
                        df= pd.read_csv(csv_file, encoding='unicode_escape', low_memory=False)
                        data_frames.append(df)
                        df = filter_by_contracts(df, contracts)
                        # Append the data frame to the list of data frames
                        filtered_and_sorted_data_frames.append(df)

print(len(filtered_and_sorted_data_frames))
result_df = pd.concat(filtered_and_sorted_data_frames)   
print(result_df)