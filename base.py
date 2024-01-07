#!/usr/bin/env python3
import os
import re
import smtplib
import pandas as pd
import platform
import subprocess
import logging
import tkinter as tk
from tkinter import filedialog
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Import Config Variables and Credentials
from config_secrets import (SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD,
                            SENDER_EMAIL, HTML_FILE_PATH, TEMP_RTF_FILE)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if platform.system() == "Windows":
    import win32com.client

# Functions

def convert_rtf_to_html_msword(rtf_text, output_dir):
    """
    Convert RTF to HTML using MS Word (Windows only)
    """
    # Ensure this is only run on Windows
    if platform.system() != "Windows":
        logging.error("MS Word conversion is only available on Windows.")
        return None

    # Path setup
    temp_rtf_file = os.path.join(output_dir, "temp.rtf")
    html_file_path = os.path.join(output_dir, "output.html")

    # Write RTF content to a temporary file
    with open(temp_rtf_file, 'w') as rtf_file:
        rtf_file.write(rtf_text)

    # Initialize MS Word Application
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False

    try:
        # Open the RTF file and save it as HTML
        doc = word.Documents.Open(temp_rtf_file)
        doc.SaveAs(html_file_path, FileFormat=8)  # 8 represents wdFormatHTML
        doc.Close()
        word.Quit()

        logging.info(f'RTF to HTML conversion complete. HTML file saved to {html_file_path}')
    except Exception as e:
        logging.error(f'Error during MS Word conversion: {e}')
        return None

    return read_and_delete_html_file(html_file_path)

def convert_rtf_to_html_libreoffice(rtf_text, output_dir):
    """
    Convert RTF to HTML using LibreOffice
    """
    # Path setup
    temp_rtf_file = os.path.join(output_dir, "temp.rtf")
    html_file_path = os.path.join(output_dir, "output.html")

    # Write RTF content to a temporary file
    with open(temp_rtf_file, 'w') as rtf_file:
        rtf_file.write(rtf_text)

    # Conversion command for LibreOffice
    conversion_command = [
        'libreoffice',
        '--headless',
        '--convert-to',
        'html',
        '--outdir',
        output_dir,
        temp_rtf_file
    ]

    try:
        subprocess.run(conversion_command, check=True)
        logging.info(f'RTF to HTML conversion complete. HTML file saved to {html_file_path}')
    except subprocess.CalledProcessError as e:
        logging.error(f'Error during LibreOffice conversion: {e}')
        return None

    return read_and_delete_html_file(os.path.join(output_dir, 'temp.html'))

def read_and_delete_html_file(file_path):
    """
    Read HTML file and delete it
    """
    try:
        with open(file_path, 'r') as html_file:
            html_content = html_file.read()
        os.remove(file_path)
        return html_content
    except FileNotFoundError as e:
        logging.error(f"HTML file not found: {e}")
        return None

def is_valid_email(email):
    # Simple regex for validating an email address, consider using a more robust solution for production code
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email)

def send_email(subject, body, to_email, attachments):
    # Using the CONFIG dictionary to access configuration settings
    smtp_server = SMTP_SERVER
    smtp_port = SMTP_PORT
    smtp_username = SMTP_USERNAME
    smtp_password = SMTP_PASSWORD
    sender_email = SENDER_EMAIL

     # Validate each email address
    for email in to_email:
        if not is_valid_email(email):
            logging.error(f"Invalid email address: {email}")
            return

    # Validation to ensure required configurations are set
    if not smtp_username or not smtp_password or not sender_email:
        logging.error("SMTP credentials or sender email not set.")
        return

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ', '.join(to_email)
    msg['Subject'] = subject

    # The body should be passed already converted to HTML, or converted before this call
    msg.attach(MIMEText(body, 'html'))

    for attachment in attachments:
        try:
            with open(attachment, "rb") as attach_file:
                part = MIMEApplication(attach_file.read(), Name=os.path.basename(attachment))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment)}"'
                msg.attach(part)
        except FileNotFoundError as e:
            logging.error(f"Attachment file not found: {e}")
            return

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, to_email, msg.as_string())
            logging.info(f"Email sent to: {', '.join(to_email)}")
    except Exception as e:
        logging.error(f"Error sending email: {e}")

def get_excel_filename(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(('.xlsx', '.xls')):
            return filename
    return None

def getTargetFolder():
    root = tk.Tk()
    root.withdraw()

    folder_path = filedialog.askdirectory(title="Select a Folder")
    print(folder_path)
    return folder_path

def main():
    # Removed hard-coded credentials
    target_folder = getTargetFolder()
    if not target_folder:
        logging.error("No target folder selected.")
        return target_folder

    excel_file = get_excel_filename(target_folder)
    if not excel_file:
        logging.error("Excel file not found in the target folder.")
        return

    excel_data = pd.read_excel(os.path.join(target_folder, excel_file))
    
    for index, row in excel_data.iterrows():
        to_email = str(row['EmailAddress']).split(',')
        subject = str(row['SubjectLine'])
        body = str(row['Body'])
        order_refs = str(row['OrderRef']).split(',')

        # Convert body from RTF to HTML
        # Decide conversion method based on OS
        if platform.system() == "Windows":
            # Use MS Word conversion
            body_html = convert_rtf_to_html_msword(body, target_folder)
        else:
            # Use LibreOffice conversion
            body_html = convert_rtf_to_html_libreoffice(body, target_folder)
        if not body_html:
            logging.error("Failed to convert body to HTML.")
            continue

        attachments = [os.path.join(target_folder, ref.strip()) for ref in order_refs]
        
        send_email(subject, body_html, to_email, attachments)

if __name__ == "__main__":
    main()
