# /////////////////////////////////////////////////////////////////////////
# //                                                                     //
# //            Book 2 CBZ Converter by KenWeTech                        //
# //                 Part 1: process books                               //
# //                                                                     //
# /////////////////////////////////////////////////////////////////////////

import os
import subprocess
import json
import time
import shutil
import re
from PyPDF2 import PdfReader
from ebooklib import epub
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

# --- Input Directory Setup ---
# Define input directory.
# Replace this with the path to the folder containing your books (EPUBs and PDFs).
# Example:input_dir = r'C:\Users\YourName\Documents\Books'
# If you are unsure where your books are, you can place this script in the same folder as your books.
# Then, you can change the input_dir to the current directory with: os.getcwd()
input_dir = os.getcwd()

# --- Configuration Flags ---
# These flags allow you to customize the script's behavior.
delete_epub = True  # Set to True to delete the original EPUB file after conversion. False keeps it.
delete_opf = True    # Set to True to delete the OPF metadata file after processing. False keeps it.
add_first_page = True  # Set to True to add "First Page" to the PDF's table of contents. False skips it.
run_organize_epub = True  # Set to True to organize the files into subfolders based on book titles. False skips it.
run_extract_toc = True    # Set to True to extract the table of contents from PDF files. False skips it.
font_size = 30  # Default font size for the converted PDF.
REMOVE_KEYWORDS = ['About the Author', 'Prologue', 'Epilogue', 'Contents', 'Notes', 'Dedication', 'Acknowledgments', 'About the Publisher', 'Copyright'] # Keywords to Remove from TOC


# =============================================================
# =           Edit Below At Your Own Risk                     =
# =============================================================

# --- Function: Color code text ---
try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init()
    COLOR = True
except ImportError:
    COLOR = False

def print_status(message, status="info"):
    if not COLOR:
        print(message)
        return
    if status == "info":
        print(Fore.CYAN + message + Style.RESET_ALL)
    elif status == "success":
        print(Fore.GREEN + message + Style.RESET_ALL)
    elif status == "error":
        print(Fore.RED + message + Style.RESET_ALL)
    elif status == "warn":
        print(Fore.YELLOW + message + Style.RESET_ALL)

# --- Function: Modify EPUB Font Size and Family ---
def modify_epub_font(epub_path):
    """Modifies the font size and font family of the EPUB before conversion."""
    book = epub.read_epub(epub_path)

    # Define the CSS style for font size and font family
    css_style = f"""body {{ font-size: {font_size}px !important; font-family: "Times New Roman", serif !important; }}"""

    # Create a new style file
    css_item = epub.EpubItem(
        file_name='styles/font-size.css',
        media_type='text/css',
        content=css_style
    )

    # Add the style to the EPUB
    book.add_item(css_item)

    # Inject the CSS into the <head> section of the HTML files
    for item in book.get_items():
        if item.get_type() == epub.EpubHtml:
            soup = BeautifulSoup(item.get_body(), 'html.parser')
            head = soup.find('head')
            link_tag = soup.new_tag('link', rel='stylesheet', href='styles/font-size.css')
            head.append(link_tag)
            item.set_body(str(soup))

    # Save the modified EPUB
    modified_epub_path = epub_path.replace('.epub', '_modified.epub')
    epub.write_epub(modified_epub_path, book)
    print_status(f"Modified EPUB saved as {modified_epub_path}", "success")
    return modified_epub_path

# --- Function: Extract Table of Contents from PDF ---
def extract_toc_from_pdf(pdf_path):
    """Extracts TOC from the PDF, ignoring specific words only for the first chapter, and adds the last page as a chapter."""
    if not run_extract_toc:
        print_status(f"Skipping TOC extraction for {pdf_path} as 'run_extract_toc' is False.", "info")
        return None

    toc_json_path = pdf_path.replace('.pdf', ' chapters.json')

    # Check if the TOC JSON already exists, and skip processing if it does
    if os.path.exists(toc_json_path):
        print_status(f"Skipping TOC extraction for {pdf_path} as TOC JSON already exists.", "info")
        return toc_json_path  # Return the existing TOC JSON path

    try:
        reader = PdfReader(pdf_path)
        toc = reader.outline if reader.outline else []
        chapter_list = []
        ignore_keywords = ['title', 'cover', 'dedication', 'title page', 'contents']
        end_keywords = ['epilogue']
        first_chapter_skipped = False
        remove_after = False  # Flag to stop adding chapters after 'epilogue' or any additional end_keyword added

        if add_first_page:
            chapter_list.append({"title": "First Page", "page": 1})

        for entry in toc:
            if isinstance(entry, list):
                continue  # Skip nested TOC entries

            title = entry.title.strip().lower()
            page_num = reader.get_destination_page_number(entry) + 1

            if not first_chapter_skipped:
                if any(title.startswith(keyword) for keyword in ignore_keywords):
                    continue  # Skip unwanted sections for the first chapter
                first_chapter_skipped = True

            # Check if the title matches 'epilogue' or any additional end_keyword added
            if any(keyword in title for keyword in end_keywords):
                remove_after = True  # Set the flag to remove this chapter and subsequent ones

            if not remove_after:
                chapter_list.append({"title": entry.title, "page": page_num})

        # Add last page as a chapter entry
        last_page = len(reader.pages)
        chapter_list.append({"title": "Last Page", "page": last_page + 1})

        if chapter_list:
            # Sort chapter_list by page number
            chapter_list.sort(key=lambda x: x['page'])

            # --- Remove Entries Based on Keywords ---
            chapter_list = [
                entry
                for entry in chapter_list
                if not any(keyword.lower() in entry['title'].lower() for keyword in REMOVE_KEYWORDS)
            ]
            #---------------------------------------

            json_path = pdf_path.replace('.pdf', ' chapters.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(chapter_list, f, ensure_ascii=False, indent=4)
            print_status(f"Saved sorted TOC data with last page entry for {pdf_path} -> {json_path}", "success")
            return json_path
        else:
            print_status(f"No chapters found to save for {pdf_path}", "warn")

    except Exception as e:
        print_status(f"Error extracting TOC from {pdf_path}: {e}", "error")
        return None

# --- Function: Convert EPUB to PDF using Calibre CLI ---
def convert_epub_to_pdf(epub_path, pdf_path):
    """Converts an EPUB file to PDF using Calibre's CLI tool."""
    command = [
        "ebook-convert", epub_path, pdf_path,
        "--pdf-default-font-size", str(font_size),
        "--margin-top", "0.1",
        "--margin-bottom", "0.1",
        "--margin-left", "0.1",
        "--margin-right", "0.1"
    ]
    print_status(f"Running command: {' '.join(command)}", "info")
    try:
        # Capture the output with explicit encoding
        result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
        print_status(f"Converted {epub_path} to {pdf_path}", "success")
        if result.stdout:
            print("Stdout:", result.stdout)
        if result.stderr:
            print("Stderr:", result.stderr)
    except subprocess.CalledProcessError as e:
        print_status(f"Error during conversion of {epub_path}: {e}", "error")
        if e.stdout:
            print("Stdout:", e.stdout.decode('utf-8', errors='ignore'))  # Attempt to decode error output
        if e.stderr:
            print("Stderr:", e.stderr.decode('utf-8', errors='ignore'))  # Attempt to decode error output

# --- Function: Organize EPUB and Related Files ---
def organize_epub_files(input_dir):
    """Organizes EPUB, PDF, OPF, and JSON files into subfolders based on book titles."""
    if not run_organize_epub:
        print_status("Skipping organize_epub_files as 'run_organize_epub' is False.", "info")
        return

    for file_name in os.listdir(input_dir):
        if file_name.lower().endswith(('.epub', '.opf', '.pdf', '.json')):
            file_path = os.path.join(input_dir, file_name)

            # Remove 'V ' from file name
            cleaned_name = file_name[2:] if file_name.startswith('V ') else file_name

            # Folder name should ignore 'Chapters'
            folder_name = os.path.splitext(cleaned_name)[0]  # Remove extension
            folder_name = re.sub(r'\s?chapters\s?\d*', '', folder_name, flags=re.IGNORECASE).strip()

            destination_folder = os.path.join(input_dir, folder_name)
            os.makedirs(destination_folder, exist_ok=True)

            new_file_path = os.path.join(destination_folder, cleaned_name)  # Keep original filename

            if os.path.abspath(file_path) != os.path.abspath(new_file_path):
                shutil.move(file_path, new_file_path)
                print_status(f"Moved '{file_name}' to '{new_file_path}'", "info")
            else:
                print_status(f"Skipping move: '{file_name}' is already in the correct folder", "info")

# --- Function: Extract Metadata from OPF ---
def extract_metadata(opf_path):
    """Extracts metadata from an OPF file."""
    metadata = {
        'title': '', 'localized_series': '', 'series': '', 'number': '', 'count': '', 'volume': '',
        'summary': '', 'publisher': '', 'year': '', 'month': '', 'day': '', 'writer': '',
        'penciller': '', 'inker': '', 'colorist': '', 'letterer': '', 'cover_artist': '',
        'editor': '', 'translator': '', 'genre': '', 'tags': '', 'web': '', 'page_count': '',
        'language': '', 'format': '', 'series_group': '', 'age_rating': '', 'gtin': ''
    }
    try:
        tree = ET.parse(opf_path)
        root = tree.getroot()
        ns = {'opf': 'http://www.idpf.org/2007/opf', 'dc': 'http://purl.org/dc/elements/1.1/'}

        def get_text(xpath):
            element = root.find(xpath, ns)
            return element.text.strip() if element is not None and element.text else ''

        summary = get_text('.//dc:description')
        if summary:
            # Remove HTML tags from summary using BeautifulSoup
            soup = BeautifulSoup(summary, 'html.parser')
            summary = soup.get_text(separator=' ', strip=True)  # get text, remove extra spaces

        metadata.update({
            'title': get_text('.//dc:title'),
            'series': get_text('.//dc:series'),
            'summary': summary,  # Use the cleaned summary
            'publisher': get_text('.//dc:publisher'),
            'writer': get_text('.//dc:creator'),
            'genre': get_text('.//dc:subject'),
            'web': get_text('.//dc:identifier'),
            'language': get_text('.//dc:language'),
            'gtin': get_text('.//dc:identifier[@opf:scheme="ISBN"]'),
        })

        for meta in root.findall('.//opf:meta', ns):
            name = meta.get('name')
            content = meta.get('content', '').strip()

            if name and content:
                if name.lower() == 'calibre:series_index':
                    metadata['number'] = content
                elif name.lower() == 'calibre:series':
                    metadata['localized_series'] = content
                elif name.lower() == 'calibre:tags':
                    metadata['tags'] = content.replace(',', '; ')

        return metadata
    except Exception as e:
        print_status(f"Error extracting metadata from {opf_path}: {e}", "error")
        return None

# --- Function: Extract Metadata from PDF ---
def extract_metadata_from_pdf(pdf_path):
    """Extracts metadata from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        metadata = reader.metadata
        extracted_metadata = {
            'title': metadata.title if metadata.title else '',
            'author': metadata.author if metadata.author else '',
            'subject': metadata.subject if metadata.subject else '',
            'producer': metadata.producer if metadata.producer else '',
            'page_count': len(reader.pages)
        }
        return extracted_metadata
    except Exception as e:
        print_status(f"Error extracting metadata from {pdf_path}: {e}", "error")
        return None

# --- Function: Create Metadata JSON ---
def create_metadata_json(file_path):
    base_name = os.path.splitext(file_path)[0]
    opf_path = base_name + '.opf'
    pdf_path = base_name + '.pdf'
    json_path = base_name + ' metadata.json'

    if os.path.exists(json_path):
        print_status(f"Skipping metadata creation for {file_path} as metadata JSON already exists.", "info")
        return

    metadata = None
    if os.path.exists(opf_path):
        metadata = extract_metadata(opf_path)
    elif os.path.exists(pdf_path):
        metadata = extract_metadata_from_pdf(pdf_path)

    if metadata:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)
        print_status(f"Metadata saved to {json_path}", "success")

# --- Function: Process Books in Directory ---
def process_books_in_directory(input_dir):
    """Processes all EPUB and PDF files in the specified directory."""
    for folder_path, _, file_names in os.walk(input_dir):
        for file_name in file_names:
            file_path = os.path.join(folder_path, file_name)
            pdf_path = os.path.join(folder_path, os.path.splitext(file_name)[0] + '.pdf')
            opf_path = os.path.join(folder_path, os.path.splitext(file_name)[0] + '.opf')

            # Process EPUB files
            if file_name.lower().endswith('.epub'):
                print_status(f"Processing EPUB file: {file_path}", "info")
                modified_epub_path = modify_epub_font(file_path)
                convert_epub_to_pdf(modified_epub_path, pdf_path)

                if os.path.exists(pdf_path) and delete_epub:
                    try:
                        os.remove(file_path)
                        print_status(f"Removed original EPUB: {file_path}", "info")
                    except Exception as e:
                        print_status(f"Error removing original EPUB file: {e}", "error")

                if os.path.exists(modified_epub_path):
                    try:
                        os.remove(modified_epub_path)
                        print_status(f"Removed modified EPUB: {modified_epub_path}", "info")
                    except Exception as e:
                        print_status(f"Error removing modified EPUB file: {e}", "error")

                create_metadata_json(file_path)

            # Process PDF files
            elif file_name.lower().endswith('.pdf'):
                print_status(f"Processing PDF file: {file_path}", "info")
                extract_toc_from_pdf(file_path)
                create_metadata_json(file_path)

            # Delete OPF files if configured
            elif file_name.lower().endswith('.opf') and delete_opf:
                try:
                    os.remove(file_path)
                    print_status(f"Removed OPF file: {file_path}", "info")
                except Exception as e:
                    print_status(f"Error removing OPF file: {e}", "error")

# --- Main Script Execution ---
if __name__ == "__main__":
    process_books_in_directory(input_dir)  # First run
    print_status("Waiting 5 seconds before re-running...", "info")
    time.sleep(5)  # Wait for 5 seconds
    print_status("Re-running the process...", "info")
    process_books_in_directory(input_dir)  # Re-run the process

    # Process files with OPF or PDF, but only if the JSON is missing.
    for folder_path, _, file_names in os.walk(input_dir):
        for file_name in file_names:
            file_path = os.path.join(folder_path, file_name)
            base_name = os.path.splitext(file_name)[0]
            opf_path = os.path.join(folder_path, base_name + '.opf')
            pdf_path = os.path.join(folder_path, base_name + '.pdf')
            json_path = os.path.join(folder_path, base_name + ' metadata.json')

            if os.path.exists(json_path):
                print_status(f"Skipping {file_name} as metadata JSON already exists.", "info")
                continue

            if os.path.exists(opf_path):
                print_status(f"Processing OPF file: {opf_path}", "info")
                create_metadata_json(opf_path)

            elif os.path.exists(pdf_path):
                print_status(f"Processing PDF file: {pdf_path}", "info")
                create_metadata_json(pdf_path)

    organize_epub_files(input_dir)  # Organize files into subfolders.

