# Bulk Email Sending Application

This Python application allows you to send emails to a list of recipients using data from an Excel sheet. It supports sending attachments, setting email subjects, and customizing email bodies.

## Features

- Send emails to multiple recipients using data from an Excel sheet.
- Attach files to each email based on attachment information in the Excel sheet.
- Customize email subjects and bodies for each recipient.

## Prerequisites

- Python 3.x installed on your system.
- Required libraries can be installed using: `pip install openpyxl`.

## Getting Started

1. Clone this repository or download the ZIP file.

2. Install the required libraries using the following command:

```cmd
pip install openpyxl
```

3. Open the `email_sender.py` file and replace the following placeholders:
- `"your_email@gmail.com"`: Your sender email address.
- `"your_password"`: Your email password or app-specific password.
- `"path_to_excel_file.xlsx"`: Path to your Excel file containing recipient data.
- `"path_to_attachments_folder"`: Path to the folder containing attachments.

4. Run the application by executing the following command:
```cmd
python email_sender.py
```

5. The application will prompt you to select a folder using a graphical interface. Choose a folder that contains the Excel sheet and attachments.

6. The application will send emails to each recipient listed in the Excel sheet with their respective attachments, subjects, and bodies.

## Security Note

It's not recommended to use your actual email password in the code. For better security, consider using app-specific passwords or OAuth for email authentication.

## Feedback and Contributions

Feel free to provide feedback or contribute to this project by creating issues or pull requests on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).