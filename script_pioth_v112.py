# Author: Maksim Dmitriev : GitHub: Mak7bit
# Date: 15/02/2024 - For Osmose Australia Pty Ltd
# script.csv - allows to read and manipulate truck data to produce a suitable out-put that later could be fed into PowerBI system
# Version:  V.04 - updated to take in a list of triggers for Date/Time recording (Ingition Off instances)
#           V.05 - new fucntions added to reduced the code size
#           V.06 - updated to take in combination of HourlyKilometeReport for a number of vehicles for a single date (as it comes out form the 
#                   Tracking Service Provider data Base)
#           V.07 - added a new option to enter the vehicle data by selecting a file, instead of providing it via command line argument
#           V.072 - script is modified to allow it to work with data how it comes out from CustomFleet. Dependecy: Report Type: Detailed History
#           V.08 - Script is addapted to be used with row unfiltered scheduled report (emailed to authors email daily)
#           V.09 - Script adjusted to keep the selection window open in order to optimise the time efficiency when working with 
#                   multiple files containing truck data until the exit button(new) is pressed.
#           V.10 - Script is edited to allow to select multiple truck-data files at once and then pass them though the code individually. 
#           V.11 - Added Osmose icons. 
#           V.112 - The colour scheme is adjusted to follow officially prescribed OSMOSE guidlines for tags. 



import csv
import sys
import re
import pandas as pd
import os
import tkinter as tk 
from tkinter import filedialog
from tkinter import * 
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.QtCore import Qt
from PIL import ImageTk, Image, ImageWin
import ctypes
#import ttkthemes


a=['Ignition Off', 'Ignition Off*']
#a='Ignition Off'
b='Ignition On'




def extract_vehicle_rego(file_path):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
        #print(data)
        rego = None
        for row in data:
            #print(len(row))
            if len(row) > 0 and re.match(r'\w{1,6}\d{1,6}', row[0]):
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
    columns_to_drop =['Address', 'City', 'State', 'Postcode','Landmark', 'Speed','Heading', 'Rssi', 'Vehicle Voltage', 'Driver HID', 'Purpose of Trip', 'Vehicle External ID', 'Logsys Work Group']
    df = pd.read_csv(file_path, delimiter=',')
    for col in columns_to_drop:
        if col in df.columns:
            df = df.drop(col, axis=1)
    #df = df.drop(df.columns[[1,2]], axis=1) # by index
    #df = df.drop(['Address', 'City', 'State', 'Postcode','Landmark', 'Speed','Heading', 'Rssi', 'Vehicle Voltage', 'Driver HID', 'Purpose of Trip', 'Vehicle External ID', 'Logsys Work Group'],axis=1)    # by name
    df = df[df['Event'].isin(['Ignition Off', 'Ignition On'])]
    # Extract the date from the second column and create a new 'Date' column
    df['Date'] = pd.to_datetime(df.iloc[:, 1], format='%Y/%m/%d %H:%M').dt.date
    # Get a list of unique dates
    date_list = list(set(df['Date'].tolist()))
    # Split the dataframe into two based on the 'Event' column
    on_df = df[df['Event'] == 'Ignition On'].groupby('Date').first().reset_index()
    off_df = df[df['Event'] == 'Ignition Off'].groupby('Date').last().reset_index()
      
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

def exit_program():
    sys.exit()

def process_file(file_name): 
    print("Processing file:", file_name)
    rego = extract_vehicle_rego(file_name)
    print("The Rego is:",rego)

    file_path = file_name
    as_df, bs_df, date_list = filter_rows(file_path)

    write_temp_data_holder(bs_df,as_df)
    merged_df = get_duration()
    merged_df['Rego'] = rego
    merged_df['Total Kms'] = merged_df['Odometer_x'] - merged_df['Odometer_y']
    print(merged_df)
    # Write temp file to see iter
    writer = pd.ExcelWriter('Temp.xlsx', engine='openpyxl')
    merged_df.to_excel(writer, sheet_name='Sheet 1', index=False)
    writer.save()
    merged_df = write_duration_file(merged_df,rego)
    read_and_update_dataframe(merged_df)

def get_file_name():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    file_name = file_path.split("/")[-1] # extract only the file name from the full path
    if file_name:
        process_file(file_name)

def get_file_names():
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames()
    file_names=[]
    if file_paths:
        for file_path in file_paths:
            file_name = file_path.split("/")[-1]
            #file_names.append(file_name)
            process_file(file_name)

#def set_app_icon(root, icon_path):
#    img = Image.open(icon_path)
#    img = img.resize((16,16), Image.ANTIALIAS)
#
#    icon = ImageWin.Icon(
#        size=16,
#        mask = ImageWin.Mask(img.covner("1")),
#        data = img.tobytes("raw", "BGRX")
#    )
#    root.wm_iconbitmap(bitmap=icon)

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
    img = img.resize((408, 120), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)
    #label = tk.Label(frame, image=img)
    #label.pack()
    label = tk.Label(frame, image=img, bg="#c7c8ca")
    

    center_x = 1100/2
    center_y = 550/2

    # Calculate the position of the label
    label_width = 408
    label_height = 120
    label_x = center_x - int(label_width / 2)
    label_y = center_y - int(label_height / 2)
    label.place(x=label_x, y=label_y) # position the label using the place method

    root.mainloop()








       