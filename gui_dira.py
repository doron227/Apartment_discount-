import os
import tkinter
import customtkinter
from tkinter import messagebox
import json
import pandas
import re
import random
import smtplib
import sys
from pathlib import Path
from dira_url_json import dira_url_json



def popup_message(kind, title, body_text):
    """
    This function generates a popup messagebox using tkinter.messagebox function. it receives:
    kind       ->    the type of the messagebox. This function was designed and tested to use only few types (showinfo,
                     showwarning, showerror).
    title      ->    The title of the message box (string).
    body_text  ->    The text in the body of the messagebox (string).

    Correct way to call this function:
            popup_message("showerror", "this is the title of the messagebox", "this is the text of the messagebox")
    """
    message_type = getattr(tkinter.messagebox, kind)
    customtkinter.CTkLabel(root, text=message_type(title, body_text)).pack()


def OTP_verification():
    '''
    This function generates a random four-digit code and send it via gmail account to a user who wishes to use the program.
    '''
    global OTP
    OTP = random.randint(1000, 9999)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    email_id = list(dictionary.values())[2]
    mail_subject = "Dira Lottery Wizard OTP code"
    mail_text = "Your OTP code is " + str(OTP)
    message = 'Subject: {}\n\n{}'.format(mail_subject, mail_text)
    server.login('diradiscountwizard@gmail.com', 'ukvzimaqprnpgfhb')
    server.sendmail('&&&&&', email_id, message)


def open_OTP_window():
    """
    This function opens the 'OTP verification' pop-up window.
    """
    global OTP_window_entry
    global OTP
    OTP_window = customtkinter.CTkToplevel(root)
    OTP_window.geometry("320x150")
    OTP_window.title("Email authentication step")
    # OTP_window.iconbitmap("appa.ico")
    OTP_window_label = customtkinter.CTkLabel(master=OTP_window, text="\n\nAn OTP code was sent to your mail.           \n"
                                            "Please type it in the field and click 'Submit' \n\n",font=(font_name, font_size*1.166))
    OTP_window_label.grid(row=0, column=0, columnspan=10)
    OTP_window_entry = customtkinter.CTkEntry(master=OTP_window)
    OTP_window_entry.grid(row=2, column=0)
    OTP_window_button = customtkinter.CTkButton(master=OTP_window, text="Submit", command=lambda: check_otp(int(OTP_window_entry.get())), font=(font_name, font_size*.8))
    OTP_window_button.grid(row=2, column=3)


def check_otp(user_otp):
    '''
    This function compare the four-digit OTP code the user typed to the random OTP code that was sent.
    If the user types the correct code, a .json file will be generated and saved in the curred working directory.
    This .json file "holds" all the information that the user typed/selected in the GUI, and will be used my the main.
    If the code doesn't match, a warning popup window appears and the .json file is not generated.
    '''
    if user_otp == OTP:
        popup_message("showinfo", "OTP code match", "Thank you for registering to Dira Lottery")
        text_file = open(os.path.join(os.getcwd(), "GUI_output.txt"), "w")
        text_file.write(json.dumps(dictionary))
        text_file.close()
        root.quit()
        file = Path("GUI_output.txt")

        if file.exists():
            with open(file, "r") as file:
                data = json.load(file)
        if data['allow automation'] == 1:
            import schedule
            import main
        else:
            import main

    else:
        popup_message("showwarning", "OTP code error", "OTP code doesn't match, please try again")


def run():
    '''
    When the user wishes to submit his form with all the relevant info he clicks this button. a dictionary containing
    all the user's details his than generated. this function checks if the email address is valid using regular expressions.
    If the email is valid it will run the functions for OTP-code verification. Otherwise, an error window will popup and
    require the user to type the mail address again.
    '''
    global save_email
    global dictionary
    dictionary = {
        'settlments': [settlement_1st_selection.get(), settlement_2nd_selection.get(), settlement_3rd_selection.get()],
        'price ranges': [
                        [settlement_1st_selection_min_combo_box.get(), settlement_1st_selection_max_combo_box.get()],
                        [settlement_2nd_selection_min_combo_box.get(), settlement_2nd_selection_max_combo_box.get()],
                        [settlement_3rd_selection_min_combo_box.get(), settlement_3rd_selection_max_combo_box.get()]
        ],
        'email': email.get(),
        'allow automation': allow_email.get(),
        'report frequency': report_freq.get(),
        'terminate reports': termminate_freq.get()
    }
    if list(dictionary.values())[3] == 0:
        popup_message("showwarning", "Automation error", "You haven't switched on Auto reports")
    if not re.compile(r"[^@]+@[^@]+\.[^@]+").match(list(dictionary.values())[2]):
        popup_message("showerror", "Email address error", "Email address is invalid.\nPlease type it again.")
    else:
        OTP_verification()
        open_OTP_window()


'''
The code section below collect all settlements identifier numbers (LamasCode) from the lottery API, and converts the numbers to english names.
This is done by comparing the identifier numbers to data taken from an API that holds all the Israeli settlements.
This API has the english name of all teh settlements. 
Therefore, in the GUI, the user is restricted to select (from a drop-down menu) only settlements which appear in the lottery 
database.
'''


url_lottery = "https://data.gov.il/api/3/action/datastore_search?resource_id=7c8255d0-49ef-49db-8904-4cf917586031&"
dira_json_data = dira_url_json(url_lottery)
current_LamasCodes = list(set((pandas.DataFrame.from_dict(dira_json_data['result']['records']))['LamasCode']))

url_settlements = 'https://data.gov.il/api/3/action/datastore_search?resource_id=d4901968-dad3-4845-a9b0-a57d027f11ab&'
settlements_data = dira_url_json(url_settlements)['result']['records']
settlements_table = pandas.DataFrame.from_dict(settlements_data)
settlements_LamasCode_to_english_dict = dict(zip(settlements_table.סמל_ישוב.astype(int), settlements_table.שם_ישוב_לועזי))

settlments_english = sorted(list(map(settlements_LamasCode_to_english_dict.get, current_LamasCodes)))


# Creating a GUI using customkinter module:
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")
root = customtkinter.CTk()
root.geometry("670x630")
root.title("Dira lottery wizard")
frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=30, padx=20)



# Variables/ lists of strings that will build the GUI interface:
numbering_order = ['1st', '2nd', '3rd']
variable_names = ['_label', '_1st_price_label', '_2nd_price_label']
default_settlements = ["TEL AVIV - YAFO", "JERUSALEM", "BE'ER SHEVA"]
price_strings = ["_min", "_max"]
price_list = list(map(str, list(range(4000, 22500, 500))))
font_name = "Verdana"
font_size = 12
price_start = "m\u00b2 price in NIS, from:"
price_end = "to:"


# This loop creates all GUI elements which are repeating
for curr_num in range(len(numbering_order)):
    font_size_counter = 0
    for var_name in range(len(variable_names)):
        name = "settlement_" + numbering_order[curr_num] + variable_names[var_name]
        if font_size_counter == 0:
            font_size = font_size/.6
        elif 0 < font_size_counter < 2:
            font_size = font_size*.6
        font_size_counter += 1
        locals()[name] = customtkinter.CTkLabel(master=frame, text=f"Select {numbering_order[curr_num]} settlement", font=(font_name, font_size))
    selection = "settlement_" + numbering_order[curr_num] + "_selection"
    locals()[selection] = tkinter.StringVar()
    locals()[selection].set(default_settlements[curr_num])
    selection_option_menu = str(selection) + "_option_menu"
    locals()[selection_option_menu] = customtkinter.CTkOptionMenu(master=frame, values=settlments_english, variable=locals()[selection])
    for price_lim in range(len(price_strings)):
        selection_price = str(selection) + str(price_strings[price_lim])
        locals()[selection_price] = tkinter.IntVar()
        if price_lim == 0:
            locals()[selection_price].set(price_list[0])
        else:
            locals()[selection_price].set(price_list[-1])
        selection_price_combo_box = str(selection_price) + "_combo_box"
        locals()[selection_price_combo_box] = customtkinter.CTkComboBox(master=frame, values=price_list, variable=locals()[selection_price])


# These GUI elements are "unique" so they are written one-by-one
email_label = customtkinter.CTkLabel(master=frame, text="Enter your email address", font=(font_name, font_size*1.33))
reports_label = customtkinter.CTkLabel(master=frame, text="Select reports frequency from the drop menu:", font=(font_name, font_size))
terminate_reports_Label = customtkinter.CTkLabel(master=frame, text="Select when to automatically unsubscribe:", font=(font_name, font_size))
email = customtkinter.CTkEntry(master=frame)
allow_email = tkinter.IntVar()
allow_automation = customtkinter.CTkSwitch(master=frame, text='Allow automated runs by "Schedule tasks"', variable=allow_email, font=(font_name, font_size))
run_button = customtkinter.CTkButton(master=frame, text="Run!", command=run, font=(font_name, font_size/.6))
receive_freqs = ["Weekly", "Bi-monthly", "Monthly"]
report_freq = tkinter.StringVar()
report_freq.set(receive_freqs[0])
reports = customtkinter.CTkOptionMenu(master=frame, values=receive_freqs, variable=report_freq)
termminate_freqs = ["1 month", "2 months", "3 months", "4 months", "5 months", "6 months", "7 months", "8 months",
                    "9 months", "10 months", "11 months", "12 months"]
termminate_freq = tkinter.StringVar()
termminate_freq.set(termminate_freqs[5])
terminate_reports = customtkinter.CTkOptionMenu(master=frame, values=termminate_freqs, variable=termminate_freq)


# This grid keep the GUI formatted as our talented designer demanded the program to look like:
settlement_1st_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10)
settlement_1st_selection_option_menu.grid(row=0, column=2, columnspan=3, padx=10, pady=10)
settlement_1st_1st_price_label.grid(row=1, column=0, columnspan=1, padx=10, pady=10)
settlement_1st_selection_min_combo_box.grid(row=1, column=1, columnspan=1, padx=10, pady=10)
settlement_1st_2nd_price_label.grid(row=1, column=2, columnspan=1, padx=10, pady=10)
settlement_1st_selection_max_combo_box.grid(row=1, column=3, columnspan=1, padx=10, pady=27)
settlement_2nd_label.grid(row=3, column=0, columnspan=3, padx=10, pady=10)
settlement_2nd_selection_option_menu.grid(row=3, column=2, columnspan=3, padx=10, pady=10)
settlement_2nd_1st_price_label.grid(row=4, column=0, columnspan=1, padx=10, pady=10)
settlement_2nd_selection_min_combo_box.grid(row=4, column=1, columnspan=1, padx=10, pady=10)
settlement_2nd_2nd_price_label.grid(row=4, column=2, columnspan=1, padx=10, pady=10)
settlement_2nd_selection_max_combo_box.grid(row=4, column=3, columnspan=1, padx=10, pady=27)
settlement_3rd_label.grid(row=6, column=0, columnspan=3, padx=10, pady=10)
settlement_3rd_selection_option_menu.grid(row=6, column=2, columnspan=3, padx=10, pady=10)
settlement_3rd_1st_price_label.grid(row=7, column=0, columnspan=1, padx=10, pady=10)
settlement_3rd_selection_min_combo_box.grid(row=7, column=1, columnspan=1, padx=10, pady=10)
settlement_3rd_2nd_price_label.grid(row=7, column=2, columnspan=1, padx=10, pady=10)
settlement_3rd_selection_max_combo_box.grid(row=7, column=3, columnspan=1, padx=10, pady=27)
email_label.grid(row=9, column=0, columnspan=3, padx=10, pady=10)
email.grid(row=9, column=2, columnspan=3, padx=10, pady=10)
reports_label.grid(row=11, column=0, columnspan=3, padx=10, pady=10)
reports.grid(row=11, column=2, columnspan=8, padx=10, pady=10)
terminate_reports_Label.grid(row=12, column=0, columnspan=3, padx=10, pady=10)
terminate_reports.grid(row=12, column=2, columnspan=8, padx=10, pady=10)
allow_automation.grid(row=13, column=0, columnspan=8, padx=10, pady=10)
run_button.grid(row=13, column=3, columnspan=3, padx=10, pady=2)
root.mainloop()
