# Author: Maksim Dmitriev : GitHub: Mak7bit
# Date: 15/02/2024 - For Osmose Australia Pty Ltd
# script.csv - allows to read and manipulate truck data to produce a suitable out-put that later could be fed into PowerBI system
# Version: V.04 - updated to take in a list of triggers for Date/Time recording (Ingition Off instances)
#          V.05 - new fucntions added to reduced the code size
#          V.06 - updated to take in combination of HourlyKilometeReport for a number of vehicles for a single date (as it comes out form the Tracking Service Provider data Base)
#          V.07 - added a new option to enter the vehicle data by selecting a file, instead of providing it via command line argument
#          V.072 - script is modified to allow it to work with data how it comes out from CustomFleet. Dependecy: Report Type: Detailed History




import csv
import sys
import re
import pandas as pd
import os
import tkinter as tk 
from tkinter import filedialog
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.QtCore import Qt


a=['Ignition Off', 'Ignition Off*']
#a='Ignition Off'
b='Ignition On'



def append_to_excel(file_path, df):
    # Load existing excel file into a pandas dataframe
    try:
        writer = pd.read_excel(file_path, engine='openpyxl')
        writer = pd.ExcelWriter(file_path, engine='openpyxl')
    except FileNotFoundError:
        writer = pd.DataFrame()
    # Check if headings of the dataframe match with the headings in the excel file
    if set(df.columns) == set(writer.columns):
        writer = writer.append(df, ignore_index=True)
        writer.to_excel(file_path, index=False)
    else:
        print("Headings in the dataframe and excel file do not match")


def fix_location_column(filename):
    with open(filename, 'rb') as f, open(filename, 'wb') as g:
        writer = csv.writer(g, delimiter=',')
        for line in f:
            row = line.split(',', 2)
            writer.writerow(row)

def average_of_column(file_name):
    with open(file_name, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
        column = [row[2] for i, row in enumerate(data) if i >= 3]
        avg = sum(map(float, column)) / len(column)
        for row in data:
            for cell in row:
                match = re.findall(r"Vehicle:\[(.*?)\]", str(cell))
                if match:
                    rego = match[0]
        return avg, rego
    
def extract_vehicle_rego(file_path):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
        #print(data)
        rego = None
        for row in data:
            if len(row) == 5 and re.match(r'\w{1,6}\d{1,6}', row[0]):
                #print(row)
                match = re.findall(r'\w{1,6}\d{1,6}', row[0])
                if match:
                    rego = match[0]
        return rego

def write_temp_data_holder(ignition_on_data, ignition_off_data):
    writer = pd.ExcelWriter('filtered_rows_new.xlsx', engine='openpyxl')
    ignition_off_data.to_excel(writer, sheet_name=a[0], index=False)
    ignition_on_data.to_excel(writer, sheet_name=b, index=False)
    writer.save()

def filter_rows(file_path):
    df = pd.read_csv(file_path, delimiter=',')
    #df = df.drop(df.columns[[1,2]], axis=1) # by index
    df = df.drop(['Address', 'City', 'State', 'Postcode','Landmark', 'Speed','Heading', 'Rssi', 'Vehicle Voltage', 'Driver HID', 'Purpose of Trip', 'Vehicle External ID', 'Logsys Work Group'],axis=1)    # by name
    df = df[df['Event'].isin(['Ignition Off', 'Ignition On'])]
    # Extract the date from the second column and create a new 'Date' column
    df['Date'] = pd.to_datetime(df.iloc[:, 1], format='%Y/%m/%d %H:%M').dt.date
    # Get a list of unique dates
    date_list = list(set(df['Date'].tolist()))
    # Split the dataframe into two based on the 'Event' column
    on_df = df[df['Event'] == 'Ignition On'].groupby('Date').last().reset_index()
    off_df = df[df['Event'] == 'Ignition Off'].groupby('Date').first().reset_index()
      
    return on_df, off_df, date_list

def get_duration():
    end_df = pd.read_excel('filtered_rows_new.xlsx', sheet_name=a[0])
    start_df = pd.read_excel('filtered_rows_new.xlsx', sheet_name=b)
    #start_df = ignition_on
    #end_df = ignition_off
    merged_df = start_df.merge(end_df, on='Date') # mergin on Date column
    #print(merged_df)
    merged_df['Date (AWST)_x'] = pd.to_datetime(merged_df['Date (AWST)_x'])
    merged_df['Date (AWST)_y'] = pd.to_datetime(merged_df['Date (AWST)_y'])
    merged_df['Duration'] = (merged_df['Date (AWST)_x'] - merged_df['Date (AWST)_y']).dt.total_seconds() # As seconds
    merged_df['Duration'] = merged_df['Duration']/60/60
    merged_df = merged_df.drop(columns=['Vehicle_x', 'Vehicle_y'])
    #print(merged_df)
    return merged_df

def update_data_base_date_as_list_member(merged_df, date_list,rego):
    for date in date_list:
        print(date)
        hourly_report_file_name = 'HourlyKilometreReport_' + date +'.xlsx'
    hourly_kilometre_report_df = pd.read_excel(hourly_report_file_name)
    merged_df['Total Kms'] = hourly_kilometre_report_df['Total']
    merged_df['Rego'] = rego
    # Removing rudimentary columns:
    merged_df = merged_df.drop(merged_df.columns[[3,6]], axis=1)

    new_file_name = 'duration_' + rego +'.xlsx'
    merged_df.to_excel(new_file_name, sheet_name='Duration', index=False, startrow=0, header=True, engine='openpyxl')

    existing_file = "data_base - dupes.xlsx"
    existing_df = pd.read_excel(existing_file)
    # Get the list of existing column names
    existing_columns = existing_df.columns
    # Read in the data you want to append to the existing file
    new_df=merged_df
 
    df = pd.concat([existing_df, new_df])
    df = df.drop_duplicates(subset=['Date', 'Rego'], keep='first')
    df.to_excel("data_base - dupes.xlsx", index=False)


def update_data_base_date_as_strftime_excel(merged_df, date_list, rego): # excel version
    existing_file = "data_base - dupes.xlsx"
    existing_df = pd.read_excel(existing_file)

    for date in date_list:
        hourly_report_file_name = 'HourlyKilometreReport_' + date.strftime('%Y-%m-%d') + '.xlsx'
        try:
            hourly_kilometre_report_df = pd.read_excel(hourly_report_file_name)
            merged_df.loc[merged_df['Date'] == date, 'Total Kms'] = hourly_kilometre_report_df['Total'].iloc[0]
        except FileNotFoundError:
            continue

    merged_df['Rego'] = rego
    # Removing rudimentary columns:
    merged_df = merged_df.drop(merged_df.columns[[3, 6]], axis=1)

    new_file_name = 'duration_' + rego + '.xlsx'
    merged_df.to_excel(new_file_name, sheet_name='Duration', index=False, startrow=0, header=True, engine='openpyxl')

    df = pd.concat([existing_df, merged_df])
    # Remove duplicate rows based on specific columns
    df = df.drop_duplicates(subset=['Date', 'Rego'], keep='first')
    df.to_excel(existing_file, index=False)

def update_data_base_date_as_strftime_csv(merged_df, date_list, rego): # csv version
    existing_file = "data_base - dupes.xlsx"
    existing_df = pd.read_excel(existing_file)

    for date in date_list:
        hourly_report_file_name = 'HourlyKilometreReport_' + date.strftime('%Y-%m-%d') + '.csv'
        try:
            hourly_kilometre_report_df = pd.read_csv(hourly_report_file_name)
            merged_df.loc[merged_df['Date'] == date, 'Total Kms'] = hourly_kilometre_report_df['Total'].iloc[0]
        except FileNotFoundError:
            continue

def update_data_base_csv(date_list, merged_df, rego):
    for date in date_list:
        #print(date)
        #hourly_report_file_name = 'HourlyKilometreReport_' + str(date) +'.csv'
        #print(hourly_report_file_name)
        try:
            hourly_kilometre_report_df = pd.read_csv(hourly_report_file_name)

            kms= hourly_kilometre_report_df.loc[hourly_kilometre_report_df['Vehicle Name'] == rego, 'Total'].iloc[0]
            print(date, ': ', kms)
            merged_df.loc[merged_df['Date'].dt.date == date, 'Total Kms'] = kms
            print(merged_df)
        except FileNotFoundError:
            continue
    return merged_df


def write_duration_file(merged_df,rego):
               # Removing rudimentary columns:
    merged_df = merged_df.drop(merged_df.columns[[3,6]], axis=1)
    #print(merged_df)
    new_file_name = 'duration_' + rego +'.xlsx'
    merged_df.to_excel(new_file_name, sheet_name='Duration', index=False, startrow=0, header=True, engine='openpyxl')

def write_duration_file(merged_df, rego):
    merged_df['Rego'] = rego
               # Removing rudimentary columns:
    merged_df = merged_df.drop(merged_df.columns[[3,6]], axis=1)
    #print(merged_df)
    new_file_name = 'duration_' + rego +'.xlsx'
    merged_df.to_excel(new_file_name, sheet_name='Duration', index=False, startrow=0, header=True, engine='openpyxl')
    return merged_df

def read_and_update_dataframe(merged_df):
    existing_file = "V:\Work Program\P - Power BI\Max\data_base_custom_fleet.xlsx"
    existing_df = pd.read_excel(existing_file)
    # Read in the data you want to append to the existing file
    new_df=merged_df
        
    df = pd.concat([existing_df, new_df])
    # Remove duplicate rows based on specific columns
    df = df.drop_duplicates(subset=['Date', 'Rego'], keep='first')
    df.to_excel("V:\Work Program\P - Power BI\Max\data_base_custom_fleet.xlsx", index=False)

def get_file_name():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    file_name = file_path.split("/")[-1] # extract only the file name from the full path
    return file_name

if __name__ == "__main__":
    #if len(sys.argv) != 2:
    #    print("Usage: python script.py <filename>.csv")
    #    sys.exit()
    #file_name = sys.argv[1]
    root = tk.Tk()
    # set the window size and position
    root.geometry("400x400+{}+{}".format(int(root.winfo_screenwidth() / 2 - 200), int(root.winfo_screenheight() / 2 - 200)))
    button = tk.Button(text='Select Truck Position Data file', command=root.quit)
    button.pack()
    root.mainloop()

    file_name = get_file_name()
    #average_speed, rego = average_of_column(file_name)
    rego = extract_vehicle_rego(file_name)
    #print("The average speed is:",average_speed)
    print("The Rego is:",rego)

    file_path = file_name
    as_df, bs_df, date_list = filter_rows(file_path)

    write_temp_data_holder(bs_df,as_df)
    #merged_df = get_duration(bs_df, as_df)
    merged_df = get_duration()
    merged_df['Rego'] = rego
    merged_df['Total Kms'] = merged_df['Odometer_x'] - merged_df['Odometer_y']
    print(merged_df)
    # Write temp file to see iter
    writer = pd.ExcelWriter('Temp.xlsx', engine='openpyxl')
    merged_df.to_excel(writer, sheet_name='Sheet 1', index=False)
    writer.save()

    #merged_df = update_data_base_csv(date_list, merged_df,rego)
    merged_df = write_duration_file(merged_df,rego)
    read_and_update_dataframe(merged_df)

       