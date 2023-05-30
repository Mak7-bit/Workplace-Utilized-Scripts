# Author: Maksim Dmitriev : GitHub: Mak7bit
# Date: 17/04/2024 - For Osmose Australia Pty Ltd
# converger.py - allows to converge 3 data frames containing information on pole inspections and itemised pricing
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





data_frames = []

def show_message():
    messagebox.showinfo('Success!', 'The Combined File has been created.')

def read_in_tasks(file_path):
    tasks_df = pd.read_excel(file_path[0],sheet_name='Sheet1')
    tasks_df['Completed On'] = pd.to_datetime(tasks_df['Completed On'])
    tasks_df = tasks_df[tasks_df['Completed On'] >='2023-04-01']
    return tasks_df

def read_in_works(file_path):
    works_df = pd.read_excel(file_path[0],sheet_name='Sheet1')
    works_df['Changed on'] = pd.to_datetime(works_df['Changed on'])
    works_df = works_df[works_df['Changed on'] >='2023-04-01']
    return works_df

def read_in_rates(file_path):
    rates_df = pd.read_excel(file_path[0],sheet_name='Rates Table')
    print(rates_df.columns)
    return rates_df

def process_files(rates):
    #compiled_df.rename(columns={'Plant Number':'AssetName'}, inplace = True)
    works_and_tasks_df = pd.merge(tasks_df,works_df, on='Assembly', how='right', indicator=True)
    works_and_tasks_df['DescEmpl.Resp.'] = works_df['DescEmpl.Resp.']
    merged_df = tasks_df.merge(rates[['Task code', 'Rate (excluding GST)']], how='left')
    works_and_tasks_df['Cost'] = merged_df['Rate (excluding GST)']

    write_to_excel(works_and_tasks_df)
    #print(works_and_tasks_df)
    #return diff_df


def get_file_name1():
    root = tk.Tk()
    root.withdraw()
    global tasks_df
    #try: 
    tasks_df = read_in_tasks(file_path=filedialog.askopenfilenames())


def get_file_name2():
    root = tk.Tk()
    root.withdraw()
    global works_df
    #try: 
    works_df = read_in_works(file_path=filedialog.askopenfilenames())

def get_file_name3():
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

    root.title('Progress Claim Compiler')
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
    select_button1 = tk.Button(frame, text='Select Tasks File', command=get_file_name1, font=label_font)
    select_button1.configure(bg="#003568", fg="#c7c8ca", activebackground="#c7c8ca", activeforeground="#003568")
    select_button1.pack(pady=(10, 0))

    # create select button 2
    select_button2 = tk.Button(frame, text='Select Work/s File', command=get_file_name2, font=label_font)
    select_button2.configure(bg="#003568", fg="#c7c8ca", activebackground="#c7c8ca", activeforeground="#003568")
    select_button2.pack(pady=(10, 0))

    # create select button 3
    select_button2 = tk.Button(frame, text='Select Rates File', command=get_file_name3, font=label_font)
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
