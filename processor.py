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
import pandas as pd


# Read in the CSV file as a DataFrame
root = tk.Tk()
root.withdraw()
file_path=filedialog.askopenfilenames()
for path in file_path:
    df =  pd.read_csv(path)

    # Convert the "Changed on" column to a datetime object
    df["Changed on"] = pd.to_datetime(df["Changed on"])

    # Create a new column for the calendar week
    df["Week"] = df["Changed on"].dt.isocalendar().week
    df["datetime_monday_week"] = df["Changed on"].dt.to_period('W').dt.start_time

    # Group by DescEmpl.Resp. and Week and count the number of unique Task codes
    counts = df.groupby(["DescEmpl.Resp.", "datetime_monday_week"])["Task code"].nunique()

    # Print the counts for each DescEmpl.Resp. and Week
    print(f"\nCounts for {path}:")
    #print(counts)
    #print(df)
    new_window = tk.Tk()
    new_window.withdraw()
    file_path = filedialog.asksaveasfilename(defaultextension='.xlsx',filetypes=[('Excel files', '*.xlsx')], title='Save As')
    if file_path:
        df.to_excel(file_path, sheet_name='Details', index=False, startrow=0, header=True, engine='openpyxl')
## Calculate the starting date of the first week in the data
#start_date = df["Changed on"].min() - pd.to_timedelta(df["Changed on"].min().dayofweek, unit="d")

## Create a new column for the starting date of each week
#df["Week Start"] = df["Changed on"] - pd.to_timedelta(df["Changed on"].dt.dayofweek, unit="d")

## Print the counts for each DescEmpl.Resp. and Week Start
#for index, count in counts.items():
#    desc, week_start = index
#    week_start = (week_start - start_date).days // 7
#    week_start = start_date + pd.to_timedelta(week_start * 7, unit="d")
#    print(f"{desc}\t{week_start}\t{count}")