import unittest
from unittest.mock import patch, mock_open, MagicMock
from base import convertRTFtoHTML, read_and_delete_html_file, send_email, get_excel_filename

class TestEmailSendingScript(unittest.TestCase):

    @patch('base.subprocess')
    def test_convert_rtf_to_html(self, mock_subprocess):
        # Mock the subprocess call to libreoffice, simulate no errors
        mock_subprocess.run.return_value = True

        rtf_test_string = r"{\rtf1\ansi This is a test RTF document.}"
        result = convertRTFtoHTML(rtf_test_string, "./tests/")
        
        # You need to adjust this based on the actual output of your conversion function
        self.assertIsNotNone(result)
        mock_subprocess.run.assert_called_once()

    @patch('builtins.open', new_callable=mock_open, read_data='html content')
    @patch('os.remove')
    def test_read_and_delete_html_file(self, mock_remove, mock_file):
        file_path = './tests/temp.html'
        result = read_and_delete_html_file(file_path)

        self.assertEqual(result, 'html content')
        mock_remove.assert_called_with(file_path)
        mock_file.assert_called_with(file_path, 'r')

    @patch('base.smtplib.SMTP')
    def test_send_email(self, mock_smtp):
        # Setup the email parameters
        subject = "Test Subject"
        body = "<p>This is a test body.</p>"
        to_email = ["test@example.com"]
        attachments = []  # Assume no attachments for simplicity

        send_email(subject, body, to_email, attachments)

        # Check that an email was attempted to be sent
        self.assertTrue(mock_smtp.called)
        instance = mock_smtp.return_value.__enter__.return_value
        instance.sendmail.assert_called_once_with(
            'divyesh1099@gmail.com', to_email, unittest.mock.ANY  # The exact message string will be complex due to MIME encoding
        )

    @patch('os.listdir')
    def test_get_excel_filename(self, mock_listdir):
        mock_listdir.return_value = ['./tests/test.xlsx', './tests/not_an_excel.txt']
        result = get_excel_filename('./tests/')
        
        self.assertEqual(result, './tests/test.xlsx')

if __name__ == '__main__':
    unittest.main()
