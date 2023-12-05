import os
import json
from PIL import Image
import pdfplumber
from modules.gpt.process.gpt_process import gpt_process
from datetime import datetime

def process_pdfs_to_text(input_directory, output_directory, start_from_file=None, end_at_file=None):
    check_directories(input_directory, output_directory)
    sorted_filenames = sorted(filter(lambda f: f.endswith(".pdf"), os.listdir(input_directory)))

    if start_from_file:
        sorted_filenames = [f for f in sorted_filenames if f >= start_from_file]
    if end_at_file:
        sorted_filenames = [f for f in sorted_filenames if f <= end_at_file]

    max_chars_per_batch = 3000
    current_batch_text = ""
    current_batch_filenames = []
    total_cost = 0

    for filename in sorted_filenames:
        extracted_text, updated_filenames = process_file(input_directory, filename, current_batch_filenames)

        if len(current_batch_text) + len(extracted_text) > max_chars_per_batch:
            if current_batch_text:
                total_cost = process_batch(current_batch_text, current_batch_filenames, output_directory, total_cost)
                current_batch_text = ""
                current_batch_filenames = []

            if len(extracted_text) > max_chars_per_batch:
                print(f"Processing large file individually: {filename}")
                total_cost = process_batch(extracted_text, [filename], output_directory, total_cost)
            else:
                current_batch_text, current_batch_filenames = start_new_batch(extracted_text, filename)
        else:
            current_batch_text += extracted_text
            current_batch_filenames = updated_filenames

    if current_batch_text:
        total_cost = process_batch(current_batch_text, current_batch_filenames, output_directory, total_cost)

    print(f"Total cost for processing: ${total_cost:.2f}")

def check_directories(input_directory, output_directory):
    if not os.path.exists(input_directory):
        print(f"Input directory does not exist: {input_directory}")
        return
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

def get_sorted_filenames(input_directory, start_from_file):
    sorted_filenames = sorted(filter(lambda f: f.endswith(".pdf"), os.listdir(input_directory)))
    if start_from_file:
        sorted_filenames = [f for f in sorted_filenames if f >= start_from_file]
    return sorted_filenames

def process_file(input_directory, filename, current_batch_filenames):
    with pdfplumber.open(os.path.join(input_directory, filename)) as pdf:
        extracted_text = ''.join(page.extract_text() for page in pdf.pages if page.extract_text())
    updated_filenames = current_batch_filenames + [filename]
    return extracted_text, updated_filenames

def process_batch(current_batch_text, current_batch_filenames, output_directory, total_cost):
    char_count = len(current_batch_text)
    print(f"Processing batch: {current_batch_filenames}, Character count: {char_count}")
    processed_text, cost = gpt_process(current_batch_text)
    total_cost += cost
    process_and_save_json(processed_text, output_directory)
    return total_cost

def start_new_batch(extracted_text, filename):
    current_batch_text = extracted_text + "\n\n"
    current_batch_filenames = [filename]
    return current_batch_text, current_batch_filenames

def save_to_json(gpt_response, output_directory):
    # Check if gpt_response is a list and contains dictionaries
    if isinstance(gpt_response, list) and all(isinstance(item, dict) for item in gpt_response):
        for email in gpt_response:
            save_email_data(email, output_directory)
    elif isinstance(gpt_response, dict):
        # If gpt_response is a single dictionary
        save_email_data(gpt_response, output_directory)
    else:
        print("Unexpected format of gpt_response.")

def save_email_data(email, output_directory):
    date_str = email.get("date", "")
    if date_str:
        date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        file_name = date_obj.strftime("%d%m%Y") + ".json"
        file_path = os.path.join(output_directory, file_name)

        data_to_write = {date_obj.strftime("%H:%M:%S"): email}

        if os.path.exists(file_path):
            with open(file_path, "r+") as file:
                data = json.load(file)
                data.update(data_to_write)
                file.seek(0)
                file.truncate()
                json.dump(data, file, indent=4)
        else:
            with open(file_path, "w") as file:
                json.dump(data_to_write, file, indent=4)

def process_and_save_json(processed_text, output_directory):
    # Split the processed text by double line breaks into potential JSON objects
    json_objects = processed_text.split('\n\n')
    
    for i, json_str in enumerate(json_objects):
        if json_str.strip():  # Ensure the string is not just whitespace
            try:
                # Correct the JSON formatting if necessary
                json_str = correct_json_format(json_str)

                # Attempt to parse the JSON string
                email_data = json.loads(json_str)
                save_to_json(email_data, output_directory)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON for batch item {i}: {e}")
                print("JSON string:", json_str)

def correct_json_format(json_str):
    # Handle common JSON formatting issues
    json_str = json_str.replace('\n', '')  # Remove newlines
    json_str = json_str.replace('}{', '},{')  # Correct missing commas between objects

    # Correct malformed JSON arrays and objects
    if json_str.startswith('{['):
        json_str = '[' + json_str[2:]
    if json_str.endswith(']}'):
        json_str = json_str[:-2] + ']'

    # Ensure the string starts with '{' or '[' and ends with '}' or ']'
    if not json_str.startswith('{') and not json_str.startswith('['):
        json_str = '{' + json_str
    if not json_str.endswith('}') and not json_str.endswith(']'):
        json_str = json_str + '}'

    return json_str


