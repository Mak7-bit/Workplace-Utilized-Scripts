# Author: Maksim Dmitriev : GitHub: Mak7bit
# Date: 11/04/2024 - For Osmose Australia Pty Ltd
# client_billing.py - allows to extract and compare the billing data against invoiced data. 
# Version: V.01 - Initila Version of the script, written in Python
#
#
#
#
#
import csv
import sys
import re
import pandas as pd
import os
import tkinter as tk 
from tkinter import filedialog, messagebox
from PIL import ImageTk, Image, ImageWin


data_frames = []

def show_message():
    messagebox.showinfo('Success!', 'The Combined File has been created.')

def reading_prog_claims(file_path):
    data_frame = pd.read_excel(file_path,sheet_name=1)
    data_frames.append(data_frame)

def write_to_excel(merged_data_frames): 
    new_window = tk.Tk()
    new_window.withdraw()
    file_path = filedialog.asksaveasfilename(defaultextension='.xlsx',filetypes=[('Excel files', '*.xlsx')], title='Save As')
    if file_path:
        merged_data_frames.to_excel(file_path, sheet_name='Claim Details', index=False, startrow=0, header=True, engine='openpyxl')
        show_message()

def get_file_names():
    root = tk.Tk()
    root.withdraw()
    #try: 
    file_paths = filedialog.askopenfilenames()
    file_names=[]
    if file_paths:
        for file_path in file_paths:
            #file_name = file_path.split("/")[-1]
            #file_names.append(file_name)
            reading_prog_claims(file_path)
    result_df = pd.concat(data_frames, ignore_index=True)
    write_to_excel(result_df)
    #except Exception as e:
        #messagebox.showerror('Error', f"Error Occured: {e}")

def exit_program():
    sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    #style = ttkthemes.ThemedStyle(root)
    #style.set_theme('plastik')

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
    title_label = tk.Label(frame, text="Progress Claim Compiler", font=title_font, fg="#003568", bg="#c7c8ca")
    title_label.pack(pady=(0, 10))

    # set the window size and position
    root.wm_iconbitmap('C:\\Users\\mdmitriev\\OneDrive - Osmose Utilities Services\\Pictures\\Or-removedbg.ico') # TaskBar Icon
    root.geometry("1100x550+{}+{}".format(int(root.winfo_screenwidth() / 2 - 450), int(root.winfo_screenheight() / 2 - 225)))

    # create select button
    select_button = tk.Button(frame, text='Select Progress Claim Data file/s', command=get_file_names, font=label_font)
    select_button.configure(bg="#003568", fg="#c7c8ca", activebackground="#c7c8ca", activeforeground="#003568")
    select_button.pack(pady=(10, 0))

    # create exit button
    exit_button = tk.Button(frame, text='Exit', command=exit_program, font=label_font)
    exit_button.configure(bg="#003568", fg="#c7c8ca", activebackground="#c7c8ca", activeforeground="#003568")
    exit_button.pack(pady=(10, 0))

    # add an image to the pop-up window using PLACE instead of PACK allows to preserve Transparency
    img = Image.open('C:\\Users\\mdmitriev\\OneDrive - Osmose Utilities Services\\Pictures\\Osmose logo (blue) - tagline.png').convert('RGBA')
    img = img.resize((975, 285), Image.LANCZOS)
    img = ImageTk.PhotoImage(img)
    label = tk.Label(frame, image=img, bg="#c7c8ca")
    label.image = img # store a reference to the image so it's not garbage-collected
    label.place(x=50, y=140) # position the label using the place method

    root.mainloop()

    