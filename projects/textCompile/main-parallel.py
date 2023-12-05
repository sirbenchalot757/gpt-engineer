import sys
import os
import concurrent.futures
from modules.image_text_processor import process_images_to_text

def divide_into_batches(files, num_batches):
    batch_size = len(files) // num_batches + (len(files) % num_batches > 0)
    return [files[i:i + batch_size] for i in range(0, len(files), batch_size)]

def process_batch(batch, input_directory, output_directory, file_type):
    start_from_file = format_filename(batch[0], file_type) if batch else None
    end_at_file = format_filename(batch[-1], file_type) if batch else None
    process_images_to_text(input_directory, output_directory, file_type, start_from_file, end_at_file)

def format_filename(number, file_type):
    if number.isdigit():
        return f"{int(number):03d}.{file_type}"
    return number

def main():
    if len(sys.argv) < 3:
        print("Usage: python main.py <directory> <file_type> [<num_processes> [<start_from> <end_at>]]")
        sys.exit(1)

    directory_name = sys.argv[1]
    file_type = sys.argv[2]
    num_processes = int(sys.argv[3]) if len(sys.argv) > 3 else 4  # Default to 4 processes

    input_directory = f"./{directory_name}/images/"
    output_directory = f"./{directory_name}/text/"

    if file_type not in ["png", "pdf"]:
        print("Unsupported file type. Use 'png' or 'pdf'.")
        sys.exit(1)

    files_to_process = sorted(filter(lambda f: f.endswith(f".{file_type}"), os.listdir(input_directory)))

    # Handle optional range arguments
    start_from = sys.argv[4] if len(sys.argv) > 4 else str(files_to_process[0]).split('.')[0]
    end_at = sys.argv[5] if len(sys.argv) > 5 else str(files_to_process[-1]).split('.')[0]

    # Generate formatted start and end filenames
    start_from_file = format_filename(start_from, file_type)
    end_at_file = format_filename(end_at, file_type)

    # Filter files based on the range
    files_to_process = [f for f in files_to_process if start_from_file <= f <= end_at_file]

    batches = divide_into_batches(files_to_process, num_processes)

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(process_batch, batch, input_directory, output_directory, file_type)
                   for batch in batches]

        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()  # This will re-raise any exception that occurred in the child process
                print(f"Batch completed with result: {result}")
            except Exception as exc:
                print(f"Batch generated an exception: {exc}")

if __name__ == "__main__":
    main()
