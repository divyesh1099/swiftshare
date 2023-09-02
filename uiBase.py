#!/usr/bin/env python3
import os
import smtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import subprocess
from functools import partial


def read_and_delete_html_file(file_path):
    try:
        with open(file_path, 'r') as html_file:
            html_content = html_file.read()
        
        # Delete the HTML file
        os.remove(file_path)

        return html_content
    except FileNotFoundError:
        return None

def convertRTFtoHTML(rtf_text):
    # Define the output HTML file path
    html_file_path = '/home/ILMSI/swiftshare/result.html'

    # Create a temporary RTF file to store the RTF data
    temp_rtf_file = '/home/ILMSI/swiftshare/temp.rtf'

    with open(temp_rtf_file, 'w') as rtf_file:
        rtf_file.write(rtf_text)

    # Convert the RTF data to HTML using LibreOffice
    conversion_command = [
        'libreoffice',
        '--headless',
        '--convert-to',
        'html',
        '--outdir',
        './',
        temp_rtf_file
    ]

    try:
        subprocess.run(conversion_command, check=True)
        print(f'RTF to HTML conversion complete. HTML file saved to {html_file_path}')
    except subprocess.CalledProcessError as e:
        print(f'Error during conversion: {e}')

    # Clean up the temporary RTF file
    os.remove(temp_rtf_file)

    # Read The Temp.html file and delete the HTML file 
    html_content = read_and_delete_html_file("./temp.html")
    return html_content


def send_email(subject, body, to_email, attachments, root: tk.Tk):
    # Email configuration
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'ajit0810'
    smtp_password = "ekcydglhzixwgxxb"
    sender_email = 'ajit0810@example.com'

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ', '.join(to_email)
    msg['Subject'] = subject
    body = convertRTFtoHTML(body)
    msg.attach(MIMEText(body, 'html'))

    for attachment in attachments:
        with open( attachment, "rb") as attach_file:
            part = MIMEApplication(attach_file.read(), Name=os.path.basename(attachment))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment)}"'
            msg.attach(part)

    # Connect to SMTP server and send email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        try:
            server.sendmail(sender_email, to_email, msg.as_string())
            tk.Label(root, text=f"Email sent to {str(to_email)}.").pack()
        except Exception as e:
            print("Error Sending Email to " + str(to_email) + ". Error: " + str(e))
            tk.Label(root, text=f"Error Sending Email to {str(to_email)}. Error {str(e)}").pack()

def getTargetFolder():
    root = tk.Tk()
    root.withdraw()

    folder_path = filedialog.askdirectory(title="Select a Folder")
    
    return folder_path

def get_excel_filename(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            return filename
    return None
    
def send_emails(rootWindow:tk.Tk):
    target_folder = getTargetFolder()
    excel_file = get_excel_filename(target_folder)
    attachments_folder = target_folder

    if excel_file is None:
        messagebox.showerror("Error", "No Excel file found in the selected folder.")
        return

    # Loading Screen
    rootWindow.title="Sending Emails"
    tk.Label(rootWindow, text="Sending Emails ...").pack()

    # Read Excel sheet
    excel_data = pd.read_excel(os.path.join(target_folder, excel_file))
    
    for index, row in excel_data.iterrows():
        to_email = row['EmailAddress'].split(',')
        subject = row['SubjectLine']
        body = row['Body']
        order_refs = row['OrderRef'].split(',')
        
        attachments = [os.path.join(attachments_folder, ref.strip()) for ref in order_refs]
        
        try:
            send_email(subject, body, to_email, attachments, rootWindow)
            tk.Label(text=f"Email sent to: {', '.join(to_email)}").pack()

        except Exception as e:
            tk.Label(text=f"Error sending email to {', '.join(to_email)}: {e}").pack()

    tk.Label(text="Email Sending Complete. Emails have been sent successfully.").pack()

def main():
    root = tk.Tk()
    root.title("Email Sender")

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)

    selectLabel = tk.Label(frame, text="Select the target folder containing Excel file and attachments:")
    selectLabel.pack()

    folder_button = tk.Button(frame, text="Select Folder", command=partial(send_emails, root))
    folder_button.pack()

    root.mainloop()

if __name__ == "__main__":
    main()