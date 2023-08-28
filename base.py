import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import openpyxl
import tkinter as tk
from tkinter import filedialog

def send_email(sender_email, sender_password, recipient_email, subject, body, attachments):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        for attachment in attachments:
            with open(attachment, "rb") as file:
                part = MIMEApplication(file.read(), Name=os.path.basename(attachment))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment)}"'
                msg.attach(part)
        
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        print(f"Email sent to {recipient_email}")
    except Exception as e:
        print(f"Error sending email to {recipient_email}: {e}")

def getTargetFolder():
    root = tk.Tk()
    root.withdraw()

    folder_path = filedialog.askdirectory(title="Select a Folder")
    
    return folder_path


def main():
    sender_email = "@gmail.com"
    sender_password = ""
    target_folder = getTargetFolder()
    excel_file = target_folder + "/RecepientsAttachments.xlsx"
    attachments_folder = target_folder+"/attachments/"
    
    wb = openpyxl.load_workbook(excel_file)
    sheet = wb.active
    
    for row in sheet.iter_rows(min_row=2, values_only=True):
        recipient_email = row[0]
        attachment_names = row[1].split(';') if row[1] else []
        subject = row[2]
        body = row[3]
        
        attachments = [os.path.join(attachments_folder, attachment_name) for attachment_name in attachment_names[0].split()]
        
        send_email(sender_email, sender_password, recipient_email, subject, body, attachments)

if __name__ == "__main__":
    main()
