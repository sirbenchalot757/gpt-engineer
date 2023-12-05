import sys
from modules.image_text_processor import process_images_to_text
from modules.pdf_text_processor import process_pdfs_to_text

def main():
    input_directory = "./yazmin/images/"
    output_directory = "./yazmin/text/"

    # Default values if no range is provided
    start_from = None
    end_at = None

    # Check if start and end range arguments are provided
    if len(sys.argv) > 2:
        start_from = f"{int(sys.argv[1]):03}.png"  # Format to '001.png', etc.
        end_at = f"{int(sys.argv[2]):03}.png"      # Format to '010.png', etc.

    process_pdfs_to_text(input_directory, output_directory, start_from, end_at)


if __name__ == "__main__":
    main()
