import PyPDF2

def repair_pdf(input_pdf_path, output_pdf_path):
    try:
        pdf = PyPDF2.PdfReader(input_pdf_path)
        writer = PyPDF2.PdfWriter()  # Use PdfWriter instead of PdfFileWriter
        
        for page_num in range(len(pdf.pages)):
            page = pdf.pages[page_num]
            writer.add_page(page)
        
        with open(output_pdf_path, 'wb') as output_file:
            writer.write(output_file)
            
        print("PDF repair successful.")
    except Exception as e:
        print(f"PDF repair failed: {str(e)}")

# Usage
input_pdf = 'OrderForwarding/22B42C003S4266B652022.pdf'
output_pdf = 'repaired.pdf'
repair_pdf(input_pdf, output_pdf)