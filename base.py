import os
import smtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import openpyxl
import tkinter as tk
from tkinter import filedialog
def send_email(subject, body, to_email, attachments):
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

    msg.attach(MIMEText(body, 'plain'))

    for attachment in attachments:
        with open(".." + attachment, "rb") as attach_file:
            part = MIMEApplication(attach_file.read(), Name=os.path.basename(attachment))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment)}"'
            msg.attach(part)

    # Connect to SMTP server and send email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        try:
            server.sendmail(sender_email, to_email, msg.as_string())
        except Exception as e:
            print("Error Sending Email to " + str(to_email) + ". Error: " + str(e))

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

def main():
    target_folder = getTargetFolder()
    excel_file = get_excel_filename(target_folder)
    attachments_folder = ".."+target_folder
    
    # Read Excel sheet
    excel_data = pd.read_excel(target_folder + "/" + excel_file)
    
    for index, row in excel_data.iterrows():
        to_email = row['EmailAddress'].split(',')
        subject = row['SubjectLine']
        body = row['Body']
        order_refs = row['OrderRef'].split(',')
        
        attachments = [os.path.join(attachments_folder, ref.strip()) for ref in order_refs]
        
        send_email(subject, body, to_email, attachments)
        print(f"Email sent to: {', '.join(to_email)}")


if __name__ == "__main__":
    main()
