import PyPDF2

# Open the PDF file in binary mode
with open('OrderForwarding/22B42C003S4266B652022.pdf', 'rb') as pdf_file:
    # Create a PDF object
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    
    # Check if the PDF is encrypted (requires a password to read)
    if pdf_reader.is_encrypted:
        pdf_reader.decrypt("")  # Provide the password if required

    # Initialize an empty string to store the text content
    text_content = ""

    # Loop through each page in the PDF
    for page_num in range(len(pdf_reader.pages)):
        # Get a specific page
        page = pdf_reader.getPage(page_num)
        
        # Extract text from the page
        page_text = page.extractText()
        
        # Append the extracted text to the overall content
        text_content += page_text

# Print the extracted text
print(text_content)
