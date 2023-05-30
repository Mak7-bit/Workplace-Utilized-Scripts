# Author: Maksim Dmitriev : GitHub: Mak7bit
# Date: 15/02/2024 - For Osmose Australia Pty Ltd
# script.csv - allows to read and manipulate truck data to produce a suitable out-put that later could be fed into PowerBI system
# Version: V.04 - updated to take in a list of triggers for Date/Time recording (Ingition Off instances)
#          V.05 - new fucntions added to reduced the code size
#          V.06 - updated to take in combination of HourlyKilometeReport for a number of vehicles for a single date (as it comes out form the Tracking Service Provider data Base)
#          V.07 - added a new option to enter the vehicle data by selecting a file, instead of providing it via command line argument
#          V.08 - added an option to keep on selecting position files for different vehicles until the exit button(new) is pressed. 
#          V.09 - the pop-up window design is adjusted to follow OSMOSE outline. 




import csv
import sys
import re
import pandas as pd
import os
import tkinter as tk 
from tkinter import filedialog, messagebox
from PIL import ImageTk, Image, ImageWin
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

def write_temp_data_holder(ignition_on_data, ignition_off_data):
    writer = pd.ExcelWriter('filtered_rows_new.xlsx', engine='openpyxl')
    ignition_off_data.to_excel(writer, sheet_name=a[0], index=False)
    ignition_on_data.to_excel(writer, sheet_name=b, index=False)
    writer.save()

def filter_rows(file_path):
    #df = pd.read_csv(file_path, delimiter=',', usecols = [i for i in range(3)]) #, quoting=csv.QUOTE_NONNUMERIC)
    #df = df[df.iloc[:, 1].isin([a,b])]

    df = pd.read_csv(file_path, delimiter=',', usecols = [i for i in range(3)]) #, quoting=csv.QUOTE_NONNUMERIC)
    df = df[df.iloc[:, 1].isin(['Ignition Off', 'Ignition Off*', 'Ignition On'])]
    #df = df.iloc[2:]
    
    df['Date'] = pd.to_datetime(df.iloc[:, 0], format='%d/%m/%Y %H:%M:%S').dt.date
    date_list = list(set(df['Date'].tolist()))
    #print(date_list)
    ab_df = df[df.iloc[:, 1].isin(a)].groupby('Date').first().reset_index()
    bs_df = df[df.iloc[:, 1] == b].groupby('Date').last().reset_index()
    # And create a list of dates: 
    return ab_df, bs_df, date_list

def get_duration():
    end_df = pd.read_excel('filtered_rows_new.xlsx', sheet_name=a[0])
    start_df = pd.read_excel('filtered_rows_new.xlsx', sheet_name=b)
    #start_df = ignition_on
    #end_df = ignition_off
    merged_df = start_df.merge(end_df, on='Date') # mergin on Date column
    merged_df['Unnamed: 0_x'] = pd.to_datetime(merged_df['Unnamed: 0_x'])
    merged_df['Unnamed: 0_y'] = pd.to_datetime(merged_df['Unnamed: 0_y'])
    merged_df['Duration'] = (merged_df['Unnamed: 0_y'] - merged_df['Unnamed: 0_x']).dt.total_seconds() # As seconds
    merged_df['Duration'] = merged_df['Duration']/60/60
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
        hourly_report_file_name = 'HourlyKilometreReport_' + str(date) +'.csv'
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
    existing_file = "V:\Work Program\P - Power BI\Max\data_base - dupes.xlsx"
    existing_df = pd.read_excel(existing_file)
    # Read in the data you want to append to the existing file
    new_df=merged_df
        
    df = pd.concat([existing_df, new_df])
    # Remove duplicate rows based on specific columns
    df = df.drop_duplicates(subset=['Date', 'Rego'], keep='first')
    df.to_excel("V:\Work Program\P - Power BI\Max\data_base - dupes.xlsx", index=False)

def select_file():
    file_path = filedialog.askopenfilename()
    print("Selected file:", file_path)


def exit_program():
    sys.exit()
    
def process_file(file_name):
    # add your code to process the selected file here
    print("Processing file:", file_name)
    average_speed, rego = average_of_column(file_name)
    print("The average speed is:",average_speed)
    print("The Reg is:",rego)

    file_path = file_name
    as_df, bs_df, date_list = filter_rows(file_path)

    write_temp_data_holder(bs_df,as_df)
    #merged_df = get_duration(bs_df, as_df)
    merged_df = get_duration()
    merged_df['Rego'] = rego
    merged_df['Total Kms'] = 0
    # Write temp file to see iter
    writer = pd.ExcelWriter('Temp.xlsx', engine='openpyxl')
    merged_df.to_excel(writer, sheet_name='Sheet 1', index=False)
    writer.save()

    merged_df = update_data_base_csv(date_list, merged_df,rego)
    merged_df = write_duration_file(merged_df,rego)
    read_and_update_dataframe(merged_df)

def get_file_name():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    file_name = file_path.split("/")[-1] # extract only the file name from the full path
    if file_name:
        process_file(file_name)
    #return file_name

def get_file_names():
    root = tk.Tk()
    root.withdraw()
    try: 
        file_paths = filedialog.askopenfilenames()
        file_names=[]
        if file_paths:
            for file_path in file_paths:
                file_name = file_path.split("/")[-1]
                #file_names.append(file_name)
                process_file(file_name)
    except Exception as e:
        messagebox.showerror('Error', f"Error Occured: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    #style = ttkthemes.ThemedStyle(root)
    #style.set_theme('plastik')

    root.title('Custom Fleet Data Processor')
    root.iconbitmap('C:\\Users\\mdmitriev\\OneDrive - Osmose Utilities Services\\Pictures\\Or-removedbg.ico') # Corner Icon 
    
    # set the background color to light blue
    root.configure(bg="#003568")

    # Set the font to a professional-looking font in the Brutalist style
    title_font = ("SegoeUI – Light", 18, "bold")
    label_font = ("SegoeUI – Light", 12)

    # Create a frame with a grey colour
    frame = tk.Frame(root, bg="#c7c8ca", padx=20, pady=20)
    frame.pack(expand=True, fill="both")


    # Add a title label to the frame
    title_label = tk.Label(frame, text="Custom Fleet Data Processor", font=title_font, fg="#003568", bg="#c7c8ca")
    title_label.pack(pady=(0, 10))

    # set the window size and position
    root.wm_iconbitmap('C:\\Users\\mdmitriev\\OneDrive - Osmose Utilities Services\\Pictures\\Or-removedbg.ico') # TaskBar Icon
    root.geometry("1100x550+{}+{}".format(int(root.winfo_screenwidth() / 2 - 450), int(root.winfo_screenheight() / 2 - 225)))

    # create select button
    select_button = tk.Button(frame, text='Select Truck Position Data file/s', command=get_file_names, font=label_font)
    select_button.configure(bg="#003568", fg="#c7c8ca", activebackground="#c7c8ca", activeforeground="#003568")
    select_button.pack(pady=(10, 0))

    # create exit button
    exit_button = tk.Button(frame, text='Exit', command=exit_program, font=label_font)
    exit_button.configure(bg="#003568", fg="#c7c8ca", activebackground="#c7c8ca", activeforeground="#003568")
    exit_button.pack(pady=(10, 0))

    # add an image to the pop-up window using PLACE instead of PACK allows to preserve Transparency
    img = Image.open('C:\\Users\\mdmitriev\\OneDrive - Osmose Utilities Services\\Pictures\\Osmose logo (blue) - tagline.png').convert('RGBA')
    img = img.resize((975, 285), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)
    #label = tk.Label(frame, image=img)
    #label.pack()
    label = tk.Label(frame, image=img, bg="#c7c8ca")
    label.image = img # store a reference to the image so it's not garbage-collected
    label.place(x=50, y=140) # position the label using the place method

    root.mainloop()

       