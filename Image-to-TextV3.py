import ocrmypdf
from PIL import Image
import fitz
import img2pdf
import os
import spacy

nlp = spacy.load('en_core_web_lg')

# Open the image file
image_directory = 'images2'
output_text_file = 'extracted_text/raw_output2.txt'
names_file = 'extracted_text/names2.txt'

def png_to_pdf(image_path, pdf_path):
    # Open the image file
    image = Image.open(image_path)
 
    # converting into chunks using img2pdf
    pdf_bytes = img2pdf.convert(image.filename)
 
    # opening or creating pdf file
    file = open(pdf_path, "wb")
 
    # writing pdf files with chunks
    file.write(pdf_bytes)
 
    # closing image file
    image.close()
 
    # closing pdf file
    file.close()
    return file

def pdf_to_pdfa(pdf_path, pdfa_path):
    ocrmypdf.ocr(pdf_path, pdfa_path, output_type='pdfa', force_ocr=True)
    return pdfa_path

def pdfa_to_txt(pdfa_path):
    # Open the PDF/A file
    pdf_document = fitz.open(pdfa_path)

    # Create an empty string to store the extracted text
    extracted_text = ""

    # Iterate over each page in the PDF
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)  # Load the page
        text = page.get_text()  # Extract text from the page
        extracted_text += text  # Append the text to the string

    return extracted_text


def process_images(image_directory, output_text_file):
    with open(output_text_file, 'w', encoding='utf-8') as text_file:
        for filename in os.listdir(image_directory):
            if filename.lower().endswith('.png' or '.jpg' or '.jpeg'):
                image_path = os.path.join(image_directory, filename)
                intermediate_pdf = 'intermediates/intermediate.pdf'
                pdfa_path = 'intermediates/output.pdf'
                
                # Convert PNG to PDF
                png_to_pdf(image_path, intermediate_pdf)
                
                # Convert PDF to PDF/A with OCR
                pdf_to_pdfa(intermediate_pdf, pdfa_path)
                
                # Extract text from PDF/A
                extracted_text = pdfa_to_txt(pdfa_path)
                
                # Write the extracted text to the text file
                text_file.write(f'Text from {filename}:\n')
                text_file.write(extracted_text)
                text_file.write('\n\n')
    
    print(f"Text extracted and saved to {output_text_file}")

def extract_names(output_text_file):
    with open(output_text_file, 'r') as file:
        raw_text = file.read()

    # Process the text with spaCy
    doc = nlp(raw_text)

    names = []

    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            # cleaned_name = re.sub(r'[A-Z]{2,}$', '', ent.text).strip()
            name = ent.text
            # Exclude names containing any digits
            if name and not any(char.isdigit() for char in name):
                names.append(name)

    print(names)

    # students = ['Rufus Corgerson', 'James Bond FBA', 'Amazon Spheres', 'JOHN SMITH']
    # filtered_names = [name for name in names if name in students]

    with open(names_file, 'w') as file:
        for name in names:
            file.write(f"{name}\n")

# Process all images in the directory
process_images(image_directory, output_text_file)
extract_names(output_text_file)
