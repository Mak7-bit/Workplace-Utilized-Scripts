# Author: Maksim Dmitriev : GitHub: Mak7bit
# Date: 25/05/2024 - For Osmose Australia Pty Ltd
# ccombination_finder.py - finds the most commond Task Code combinations for pole inspections
# Version:  V.01 -  Initial Code 


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
import matplotlib.pyplot as plt 




data_frames = []

def show_message():
    messagebox.showinfo('Success!', 'The Combined File has been created.')


def read_in_tasks(file_path):
    tasks_df = pd.read_excel(file_path[0],sheet_name='Sheet1')
    tasks_df['Created on'] = pd.to_datetime(tasks_df['Created on']).dt.date
    tasks_df = tasks_df[tasks_df['Task code'] != 'ZZZZ']
    return tasks_df

def read_in_tasks_wrapper():
    root = tk.Tk()
    root.withdraw()
    #try: 
    df = read_in_tasks(file_path=filedialog.askopenfilenames())
    
    return df

def read_in_rates_wrapper():
    root = tk.Tk()
    root.withdraw()
    #try: 
    df = read_in_rates(file_path=filedialog.askopenfilenames())
    
    return df

def read_in_rates(file_path): 
    rates_df = pd.read_excel(file_path[0],sheet_name='Rates Table')
    return rates_df



def process_files(tasks, rates_df):
    # Group the DataFrame by 'Assembly' and count the frequency of each 'Task code'
    #frequency_table = tasks.groupby('Assembly')['Task code'].value_counts()

    # Group the DataFrame by 'Assembly' and create a new column with combined 'Task code' values
    tasks['Task codes combination'] = tasks.groupby('Assembly')['Task code'].transform(lambda x: '|'.join(sorted(x)))

    # Count the frequency of unique combinations of 'Task codes' for each 'Assembly'
    frequency_table = tasks.groupby('Task codes combination')['Assembly'].nunique().reset_index(name='Frequency')

    # Add a new column 'Total Unit Cost' to the frequency_table
    frequency_table['Total Unit Cost'] = 0

    # Iterate through each row in the frequency_table
    for index, row in frequency_table.iterrows():
        task_codes = row['Task codes combination'].split('|')
        total_cost = 0
        # Iterate through each task code and sum the corresponding unit cost from the rates_df
        for task_code in task_codes:
            unit_cost = rates_df.loc[rates_df['Task code'] == task_code, 'Unit Cost'].values
            if len(unit_cost) > 0:
                total_cost += unit_cost[0]
        frequency_table.at[index, 'Total Unit Cost'] = total_cost



    

    # Print the frequency table
    #print(frequency_table)
    return frequency_table

def write_to_file(frequency_table):
    root = tk.Tk()
    root.withdraw()

    # Choose the destination file path using a file dialog
    save_path = filedialog.asksaveasfilename(defaultextension='.xlsx')

    # Write the frequency table to Excel
    frequency_table.to_excel(save_path)

    # Show a pop-up window with a success message
    tk.messagebox.showinfo("File Saved", "Frequency table saved to Excel successfully!")

    # Destroy the root window
    root.destroy()

def main(): 
    tasks = read_in_tasks_wrapper()
    rates = read_in_rates_wrapper()
    freq_table = process_files(tasks, rates)
    write_to_file(freq_table)

if __name__ == "__main__":
    main()
