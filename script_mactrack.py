# Author: Maksim Dmitriev : GitHub: Mak7bit
# Date: 19/04/2024 - For Osmose Australia Pty Ltd
# script_mactrack.csv - allows to read and manipulate truck data to produce a suitable out-put that later could be fed into PowerBI system
# Version: V.01 - Adopting new approach, trying to write initial script to process thedata in new format. 
#
#




import csv
import sys
import time
import re
import pandas as pd
import os
import tkinter as tk 
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import * 
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.QtCore import Qt
from PIL import ImageTk, Image, ImageWin
import ctypes
import io
from threading import Thread
import subprocess
import math
import numpy as np



def show_message():
    messagebox.showinfo('Success!', 'The Data File has been updated.')

def write_to_excel(df): 
    new_window = tk.Tk()
    new_window.withdraw()
    file_path = filedialog.asksaveasfilename(defaultextension='.xlsx',filetypes=[('Excel files', '*.xlsx')], title='Save As')
    if file_path:
        df.to_excel(file_path, sheet_name='Processed Data', index=False, startrow=0, header=True, engine='openpyxl')
        show_message()

def write_temp_data_holder(ignition_on_data, ignition_off_data):
    writer = pd.ExcelWriter('filtered_rows_new.xlsx', engine='openpyxl')
    ignition_off_data.to_excel(writer, sheet_name=a[0], index=False)
    ignition_on_data.to_excel(writer, sheet_name=b, index=False)
    writer.save()

def filter_rows(file_path):
    columns_to_drop =['Max Speed (km/h)', 'Start Location', 'End Location']
    df = pd.read_excel(file_path, skiprows=3, header=0)
    #df = pd.read_csv(file_path, delimiter=',')
    for col in columns_to_drop:
        if col in df.columns:
            df = df.drop(col, axis=1)
    # remove the rows containing "Total"
    #df = df[~df.iloc[:, 2].str.contains('Total')]
    #df = df[~df.iloc[:, 1].str.contains('Total')]
    df = df[~df.apply(lambda x: x.str.contains('Total')).any(axis=1)]


    # remove empty rows & repeating headers
    df = df.dropna(how='all')
    df = df[df.iloc[:,0] != 'Asset Type']
    # Reset the index
    df.reset_index(drop=True, inplace=True)  
    # Extract the date from the seventh column and create a new 'Date' column
    df['Date'] = pd.to_datetime(df.iloc[:, 6], format='%Y/%m/%d %H:%M').dt.date
    # Get a list of unique dates
    date_list = list(set(df['Date'].tolist()))
    #write_to_excel(df) # 1
    return date_list, df

def get_duration(df):
    # create a column to store Rego and populate it with NaN values
    df['Rego'] = np.nan

    #Loop through DataFrame rows
    temp_asset_value = None
    for index, row in df.iterrows():
      #temp_asset_value = None
      # Check if Asset value is not empty
      #if row['Asset'] != '':
      #if temp_asset_value is not None and not math.isnan(temp_asset_value):
      if not pd.isnull(row["Asset"]):
          # If it isn't, assign it to temporary variable
          temp_asset_value = row['Asset']
          #df.loc[index, 'Rego'] = temp_asset_value
          #print(f'Temp Asset Value: ', temp_asset_value)
          #print(f'temp_asset_value.type: ', type(temp_asset_value))

      # Check if temporary Asset value is None and if it is contained in the Description string
      if temp_asset_value is not None and str(temp_asset_value) in str(row['Description']):
          # If it is, assign it to the Rego variable and break out of the loop
          df.loc[index, 'Rego'] = temp_asset_value
    print(df['Rego'])
    #write_to_excel(df) # 2
    #df['Duration'] = pd.to_datetime(df['Duration'], format='%H:%M:%S')
    #df['Duration'] = pd.to_timedelta(df["Duration"])

    # convert Duration to seconds before summation
    df['Duration'] = df['Duration'].apply(lambda x: (x.hour * 60 + x.minute) * 60 + x.second)
    #seconds = (t.hour * 60 + t.minute) * 60 + t.second
    result_df = df.loc[:, ['Rego',
                           'Date', 
                           'Duration',
                           'Distance (km)', 
                           'Latitude', 
                           'Longitude']]
    # Summing for each data and creating an array of coordinates for each date:
    result_df = df.groupby(['Rego', 'Date']).agg({'Duration': 'sum', 'Distance (km)': 'sum'}).reset_index()
    coordinates = df.groupby('Date')[['Latitude', 'Longitude']].apply(lambda x: x.values.tolist()).reset_index(name='Coordinates')
    result_df = result_df.merge(coordinates, on='Date') 
    result_df['Duration'] = df['Duration'] / 3600
    #result_df = df.loc[:'Duration'].div(60).round(2)                                                                                            ## We Stopped here ##
    #write_to_excel(result_df) # 3
    #merged_df['Date (AWST)_x'] = pd.to_datetime(merged_df['Date (AWST)_x'])
    #merged_df['Date (AWST)_y'] = pd.to_datetime(merged_df['Date (AWST)_y'])
    #merged_df['Duration'] = (merged_df['Date (AWST)_x'] - merged_df['Date (AWST)_y']).dt.total_seconds() # As seconds
    #merged_df['Duration'] = merged_df['Duration']/60/60
    #merged_df = merged_df.drop(columns=['Vehicle_x', 'Vehicle_y'])
    #print(merged_df)
    return result_df



def write_duration_file(merged_df, rego):
    merged_df['Rego'] = rego
               # Removing rudimentary columns:
    merged_df = merged_df.drop(merged_df.columns[[3,6]], axis=1)
    #print(merged_df)
    new_file_name = 'duration_' + rego +'.xlsx'
    merged_df.to_excel(new_file_name, sheet_name='Duration', index=False, startrow=0, header=True, engine='openpyxl')
    return merged_df

def read_and_update_dataframe(merged_df):
    existing_file = "V:\Work Program\P - Power BI\Max\MacTrack\data_base_mactrack.xlsx"
    existing_df = pd.read_excel(existing_file)
    # Read in the data you want to append to the existing file
    new_df=merged_df
        
    df = pd.concat([existing_df, new_df])
    # Remove duplicate rows based on specific columns
    df = df.drop_duplicates(subset=['Date', 'Rego'], keep='first')
    df.to_excel("V:\Work Program\P - Power BI\Max\MacTrack\data_base_mactrack.xlsx", index=False)

def exit_program():
    sys.exit()

def process_file(file_name): 
    print("Processing file:", file_name)

    file_path = file_name
    date_list, data_frame = filter_rows(file_path)

    merged_df = get_duration(data_frame)
    read_and_update_dataframe(merged_df)
    show_message()
    

def get_file_name():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    file_name = file_path.split("/")[-1] # extract only the file name from the full path
    if file_name:
        process_file(file_name)

def get_file_names():
    #try:
        root = tk.Tk()
        root.withdraw()
        file_paths = filedialog.askopenfilenames()
        file_names=[]
        if file_paths:
            for file_path in file_paths:
                file_name = file_path.split("/")[-1]
                #file_names.append(file_name)
                process_file(file_name)
    #except Exception as e:
    #    messagebox.showerror('Error', f"Error Occured: {e}")

def update_output():
     # continuously update the output text widget with the console output
    while True:
        line = sys.stdout.readline()
        if not line:
            break
        output.insert("end", line)
        output.see("end")



class ConsoleRedirector(io.StringIO):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.configure(state='normal')
        self.text_widget.insert('end', message)
        self.text_widget.see('end')
        self.text_widget.configure(state='disabled')


def main():        
        ## Create the Tkinter app and a Text widget

        root = tk.Tk()
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
        title_label = tk.Label(frame, text="MacTrack Data Processor", font=title_font, fg="#003568", bg="#c7c8ca")
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
        img = img.resize((408, 120), Image.LANCZOS)
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

if __name__ == "__main__":
    main()