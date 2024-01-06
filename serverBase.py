#!/usr/bin/env python3
import os
import re
import smtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import tkinter as tk
from tkinter import filedialog
import subprocess
import logging

# Import Config Variables and Credentials
from config_secrets import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SENDER_EMAIL, HTML_FILE_PATH, TEMP_RTF_FILE

# It's good practice to set up logging instead of using print statements
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Removed hardcoded paths and credentials
# Ideally, these should be configured in a separate config file or environment variables


def convertRTFtoHTML(rtf_text, output_dir):
    # Using the CONFIG dictionary to access configuration settings
    temp_rtf_file = TEMP_RTF_FILE
    html_file_path = HTML_FILE_PATH

    with open(temp_rtf_file, 'w') as rtf_file:
        rtf_file.write(rtf_text)

    # Convert the RTF data to HTML using LibreOffice
    conversion_command = [
        'libreoffice',
        '--headless',
        '--convert-to',
        'html',
        '--outdir',
        output_dir,
        temp_rtf_file
    ]
    print("Running command:", ' '.join(conversion_command))  # Debug print
    try:
        subprocess.run(conversion_command, check=True)
        logging.info(f'RTF to HTML conversion complete. HTML file saved to {html_file_path}')
    except subprocess.CalledProcessError as e:
        logging.error(f'Error during conversion: {e}')
        return None
    except Exception as e:
        print(e)

    # Cleanup is now handled in a separate function to encapsulate functionality
    return read_and_delete_html_file(os.path.join(output_dir, 'temp.html'))
    
def read_and_delete_html_file(file_path):
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
    folder_path = "D:/DO NOT TOUCH/bulkEmail/swiftshare/OrderForwarding/OrderForwarding"
    return folder_path

def main():
    # Removed hard-coded credentials
    target_folder = getTargetFolder()
    if not target_folder:
        logging.error("No target folder selected.")
        return

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
        body_html = convertRTFtoHTML(body, target_folder)
        if not body_html:
            logging.error("Failed to convert body to HTML.")
            continue

        attachments = [os.path.join(target_folder, ref.strip()) for ref in order_refs]
        
        send_email(subject, body_html, to_email, attachments)

if __name__ == "__main__":
    main()
