import os
from PIL import Image
import pytesseract
import pdfplumber

def process_file(input_directory, filename, current_batch_filenames, file_type):
    if file_type == "png":
        # Logic to process a PNG file and return the result
        return process_png(input_directory, filename, current_batch_filenames)
    elif file_type == "pdf":
        # Logic to process a PDF file and return the result
        return process_pdf(input_directory, filename, current_batch_filenames)
    else:
        print(f"Unsupported file type: {file_type}")
        return None, current_batch_filenames  # Return a tuple with None for extracted_text


def process_png(input_directory, filename, current_batch_filenames):
    img = Image.open(os.path.join(input_directory, filename))
    extracted_text = pytesseract.image_to_string(img)
    updated_filenames = current_batch_filenames + [filename]
    return extracted_text, updated_filenames

def process_pdf(input_directory, filename, current_batch_filenames):
    with pdfplumber.open(os.path.join(input_directory, filename)) as pdf:
        extracted_text = ''.join(page.extract_text() for page in pdf.pages if page.extract_text())
    updated_filenames = current_batch_filenames + [filename]
    return extracted_text, updated_filenames