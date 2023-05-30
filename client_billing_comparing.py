# Author: Maksim Dmitriev : GitHub: Mak7bit
# Date: 11/04/2024 - For Osmose Australia Pty Ltd
# client_billing_comparing.py - allows to comapre the extracted progress claim data against the Reviewed & Approved Items
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



# Local Functions: 

def show_message():
    messagebox.showinfo('Success!', 'Completed.')

def read_in_reviewed_claim(file_path):
    reviewed_claim_df = pd.read_excel(file_path[0],sheet_name='AssetActivityReinforcing_View')
    reviewed_claim_df['ActivityDate'] = pd.to_datetime(reviewed_claim_df['ActivityDate'])
    reviewed_claim_df = reviewed_claim_df[reviewed_claim_df['ActivityDate'] >='2023-01-01']
    return reviewed_claim_df

def read_in_compiled_claim(file_path):
    compiled_claim_df = pd.read_excel(file_path[0],sheet_name='Claim Details')
    return compiled_claim_df

def compare_the_files(compiled_df, for_review_df):
    #print(repr(compiled_df.columns))
    #print(repr(for_review_df.columns))
    #compiled_df = compiled_df.rename(columns={'Plant Number':'AssetName'}) # rename the column with Asset Names to match the name in the second df. 
    compiled_df.rename(columns={'Plant Number':'AssetName'}, inplace = True)
    #print(repr(compiled_df.columns))
    #print(repr(for_review_df.columns))
    diff_df = pd.merge(compiled_df,for_review_df, on='AssetName', how='right', indicator=True)
    diff_df = diff_df[diff_df['_merge'] == 'right_only'].drop('_merge', axis=1)
    return diff_df


def get_file_name1():
    root = tk.Tk()
    root.withdraw()
    global compiled_claim_df
    #try: 
    compiled_claim_df = read_in_compiled_claim(file_path=filedialog.askopenfilenames())


def get_file_name2():
    root = tk.Tk()
    root.withdraw()
    #try: 
    reviewed_claim_df = read_in_reviewed_claim(file_path=filedialog.askopenfilenames())
    diff_df = compare_the_files(compiled_claim_df, reviewed_claim_df)
    write_to_excel(diff_df)
    #except Exception as e:
        #messagebox.showerror('Error', f"Error Occured: {e}")


def write_to_excel(merged_data_frames): 
    new_window = tk.Tk()
    new_window.withdraw()
    file_path = filedialog.asksaveasfilename(defaultextension='.xlsx',filetypes=[('Excel files', '*.xlsx')], title='Save As')
    if file_path:
        merged_data_frames.to_excel(file_path, sheet_name='Claim Details', index=False, startrow=0, header=True, engine='openpyxl')
        show_message()


def exit_program():
    sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    #style = ttkthemes.ThemedStyle(root)
    #style.set_theme('plastik')

    root.title('Progress Claim - Comparator')
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
    title_label = tk.Label(frame, text="Progress Claim Comparator", font=title_font, fg="#003568", bg="#c7c8ca")
    title_label.pack(pady=(0, 10))

    # set the window size and position
    root.wm_iconbitmap('C:\\Users\\mdmitriev\\OneDrive - Osmose Utilities Services\\Pictures\\Or-removedbg.ico') # TaskBar Icon
    root.geometry("1100x550+{}+{}".format(int(root.winfo_screenwidth() / 2 - 450), int(root.winfo_screenheight() / 2 - 225)))

    # create select button 1
    select_button1 = tk.Button(frame, text='Select Progress Claim compiled file', command=get_file_name1, font=label_font)
    select_button1.configure(bg="#003568", fg="#c7c8ca", activebackground="#c7c8ca", activeforeground="#003568")
    select_button1.pack(pady=(10, 0))

    # create select button 2
    select_button2 = tk.Button(frame, text='Select Progress Claim Review file', command=get_file_name2, font=label_font)
    select_button2.configure(bg="#003568", fg="#c7c8ca", activebackground="#c7c8ca", activeforeground="#003568")
    select_button2.pack(pady=(10, 0))

    # create exit button
    exit_button = tk.Button(frame, text='Exit', command=exit_program, font=label_font)
    exit_button.configure(bg="#003568", fg="#c7c8ca", activebackground="#c7c8ca", activeforeground="#003568")
    exit_button.pack(pady=(10, 0))

    # add an image to the pop-up window using PLACE instead of PACK allows to preserve Transparency
    img = Image.open('C:\\Users\\mdmitriev\\OneDrive - Osmose Utilities Services\\Pictures\\Osmose logo (blue) - tagline.png').convert('RGBA')
    img = img.resize((int(975/2), int(285/2)), Image.LANCZOS)
    img = ImageTk.PhotoImage(img)
    label = tk.Label(frame, image=img, bg="#c7c8ca")
    label.image = img # store a reference to the image so it's not garbage-collected
    label.place(x=300, y=220) # position the label using the place method

    root.mainloop()
