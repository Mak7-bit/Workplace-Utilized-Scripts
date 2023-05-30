# Author: Maksim Dmitriev : GitHub: Mak7bit
# Date: 17/04/2024 - For Osmose Australia Pty Ltd
# converger.py - allows to conver 3 data frames comntaining information on pole inspections and itemised pricing
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
    #tasks_df = tasks_df[tasks_df['Completed On'] >='2023-04-01']
    return tasks_df

def read_in_works(file_path):
    works_df = pd.read_excel(file_path[0],sheet_name='Sheet1')
    works_df['Changed on'] = pd.to_datetime(works_df['Changed on']).dt.date
    works_df = works_df[works_df['Changed on'] >='2023-04-01']
    return works_df

def read_in_rates(file_path):
    rates_df = pd.read_excel(file_path[0],sheet_name='Rates Table')
    print(rates_df.columns)
    return rates_df

def read_in_inspectors(file_path):
    inspectors_df = pd.read_excel(file_path[0], sheet_name='Sheet1')
    return inspectors_df

def create_inspector_cost_matrix():
    pay_matrix = {
    'Day of Week': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
    'Hours Worked': [10,10,10,10,8,6], # 8 hours + 2 hours of 1.5 rate Over-Time; Saturday: 2 hours of 1.5 OT + 6 hours of 2.0 OT
    'Pay': [418, 418, 418, 418, 342, 418],
    }

    global pay_matrix_df
    pay_matrix_df = pd.DataFrame(pay_matrix)

    # calculate total cost
    pay_matrix_df['Super'] = pay_matrix_df['Pay'] * 0.105
    pay_matrix_df['Payroll Tax'] = pay_matrix_df['Pay'] * 0.05
    pay_matrix_df['Total Cost'] = pay_matrix_df['Pay'] + pay_matrix_df['Super'] + pay_matrix_df['Payroll Tax']

def produce_profitability_plot(data_frame): 
    # Group by the categorical column
    groups = data_frame.groupby('Inspector Name')
    # name the plot:
    plotname = 'Profitability for each inspector by Date: APR+MAY-23'
    # Create a scatter plot for each group
    fig, ax = plt.subplots()
    for name, group in groups:
        ax.scatter(group['Created on'], group['Profitability'], label=name)
        ax.plot(group['Created on'], group['Profitability'], linestyle='--')

    # Add axis labels and title
    plt.xlabel('Date')
    plt.ylabel('Profitability')
    plt.title(plotname)
    plt.legend()
    plt.savefig('Profitability for each inspector by Date APR+MAY-23.png')
    plt.show()

def process_files(rates):
    #compiled_df.rename(columns={'Plant Number':'AssetName'}, inplace = True)
    #works_and_tasks_df = pd.merge(tasks_df,works_df, on='Assembly', how='right', indicator=True)
    #tasks_and_rates['DescEmpl.Resp.'] = works_df['DescEmpl.Resp.']
    merged_df = tasks_df.merge(rates[['Task code', 'Rate (excluding GST)']], how='left')
    tasks_df['Cost'] = merged_df['Rate (excluding GST)']

    # get inspector names using their T-numbers:
    merged_names = tasks_df.merge(inspectors_df[['Created by', 'name']], how='left')
    tasks_df['Inspector Name'] = merged_names['name']
    write_to_excel(tasks_df)
    tasks_and_rates = tasks_df
    #write_to_excel(tasks_and_rates)

    # Count Points by week: 
    # group the data by both the 'name' and 'date' columns and sum the 'cost' column
    result = tasks_and_rates.groupby(['Inspector Name', 'Created on']).sum(['Cost']).reset_index()
    #result['Created on'] = result.to_datetime(result['Created on'])
    result['Day of Week'] = result['Created on'].apply(lambda x: x.strftime('%A'))
    result = result.rename(columns={'Cost' : 'Revenue'})
    create_inspector_cost_matrix()
    merge_by_weekday = result.merge(pay_matrix_df[['Day of Week', 'Total Cost']], how='left')
    result['Inspector Cost'] = merge_by_weekday['Total Cost']
    print(result)
    result['Profitability'] = result['Revenue'] - result['Inspector Cost']
    results = result.drop(['Notification', 'Sort number', 'Completed On'], axis=1, inplace=True)
    write_to_excel(result)
    produce_profitability_plot(result)




def get_tasks():
    root = tk.Tk()
    root.withdraw()
    global tasks_df
    #try: 
    tasks_df = read_in_tasks(file_path=filedialog.askopenfilenames())

def get_inspector_names():
    root = tk.Tk()
    root.withdraw()
    global inspectors_df
    #try: 
    inspectors_df = read_in_inspectors(file_path=filedialog.askopenfilenames())

def get_works():
    root = tk.Tk()
    root.withdraw()
    global works_df
    #try: 
    works_df = read_in_works(file_path=filedialog.askopenfilenames())

def get_rates():
    root = tk.Tk()
    root.withdraw()
    #try: 
    rates_df = read_in_rates(file_path=filedialog.askopenfilenames())
    ###
    process_files(rates_df)


def write_to_excel(merged_data_frames): 
    new_window = tk.Tk()
    new_window.withdraw()
    file_path = filedialog.asksaveasfilename(defaultextension='.xlsx',filetypes=[('Excel files', '*.xlsx')], title='Save As')
    if file_path:
        merged_data_frames.to_excel(file_path, sheet_name='Details', index=False, startrow=0, header=True, engine='openpyxl')
        show_message()


def exit_program():
    sys.exit()


def main(): 
    root = tk.Tk()

    root.title('Ausgrid Inspections - Incentives')
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
    title_label = tk.Label(frame, text="Ausgrid Inspections - Incentivce Point Counter", font=title_font, fg="#003568", bg="#c7c8ca")
    title_label.pack(pady=(0, 10))

    # set the window size and position
    root.wm_iconbitmap('C:\\Users\\mdmitriev\\OneDrive - Osmose Utilities Services\\Pictures\\Or-removedbg.ico') # TaskBar Icon
    root.geometry("1100x550+{}+{}".format(int(root.winfo_screenwidth() / 2 - 450), int(root.winfo_screenheight() / 2 - 225)))

    # create select button 1
    select_button1 = tk.Button(frame, text='Select Tasks File', command=get_tasks, font=label_font)
    select_button1.configure(bg="#003568", fg="#c7c8ca", activebackground="#c7c8ca", activeforeground="#003568")
    select_button1.pack(pady=(10, 0))

    # create select button 2
    select_button2 = tk.Button(frame, text='Select inspector t-number matrix File', command=get_inspector_names, font=label_font)
    select_button2.configure(bg="#003568", fg="#c7c8ca", activebackground="#c7c8ca", activeforeground="#003568")
    select_button2.pack(pady=(10, 0))

    # create select button 3
    select_button2 = tk.Button(frame, text='Select Rates File', command=get_rates, font=label_font)
    select_button2.configure(bg="#003568", fg="#c7c8ca", activebackground="#c7c8ca", activeforeground="#003568")
    select_button2.pack(pady=(10, 0))

    # create exit button
    exit_button = tk.Button(frame, text='Exit', command=exit_program, font=label_font)
    exit_button.configure(bg="#003568", fg="#c7c8ca", activebackground="#c7c8ca", activeforeground="#003568")
    exit_button.pack(pady=(10, 0))

    # add an image to the pop-up window using PLACE instead of PACK allows to preserve Transparency
    img = Image.open('C:\\Users\\mdmitriev\\OneDrive - Osmose Utilities Services\\Pictures\\Osmose logo (blue) - tagline.png').convert('RGBA')
    img = img.resize((684, 200), Image.LANCZOS)
    img = ImageTk.PhotoImage(img)
    label = tk.Label(frame, image=img, bg="#c7c8ca")
    label.image = img # store a reference to the image so it's not garbage-collected
    label.place(x=220, y=240) # position the label using the place method

    root.mainloop()

if __name__ == "__main__":
    main()







# 'dataset' holds the input data for this script
# Traverse thru (3) and for each name(i) compare Client_req to Client_req in (2); 
#     if no match:
#        appned row from (2) with name(i) with Current = NO


#import pandas as pd
## find all unique instances of NAME, COURSE_NAME_AND_ID, and Course Description & ID
#names = dataset['NAME(3)'].unique()
#courses = dataset['COURSE_NAME_AND_ID(3)'].unique()
#descriptions = dataset['Course Description & ID'].unique()
#
## loop through each unique NAME and COURSE_NAME_AND_ID
#for name in names:
#    for course in courses:
#        # check if there exists a row with COURSE_NAME_AND_ID that matches an instance of Course Description & ID
#        if any(dataset.loc[(dataset['NAME(3)']==name) & (dataset['COURSE_NAME_AND_ID(3)']==course)]['Course Description & ID'].isin(descriptions)):
#            pass
#        else:
#            # append a row with the same NAME and COURSE_NAME_&_ID that will have 'NO' in column CURRENT
#            dataset = dataset.append({'NAME(3)': name, 'COURSE_NAME_AND_ID(3)': course, 'Course Description & ID': '', 'CURRENT(3)': 'NO'}, ignore_index=True)

