import sys
import zipfile
import pandas as pd
import os

def read_csv_from_zip(zip_file_name):
    with zipfile.ZipFile(zip_file_name, 'r') as zip_ref:
        files = zip_ref.namelist()
        csv_file_name = None
        for file in files:
            if file.endswith('.csv'):
                csv_file_name = file
                break
        if csv_file_name:
            csv_file = zip_ref.open(csv_file_name)
            df = pd.read_csv(csv_file)
            return df
        else:
            return None

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

def main():
    if len(sys.argv) < 2:
        print("Please specify the name of the zip file as an argument")
        return
    
    zip_file_name = sys.argv[1]
    df = read_csv_from_zip(zip_file_name)
    print(df)
    if df is not None:
        contracts = ['C46972']
        df = filter_by_contracts(df, contracts)
        df = clean_pick_id(df)
        #print(df)
        save_to_excel(df, "V:\\Work Program\\P - Power BI\\Assets\\data_frame_C46972")
    else:
        print("No CSV file found in the zip file")

if __name__ == '__main__':
    main()