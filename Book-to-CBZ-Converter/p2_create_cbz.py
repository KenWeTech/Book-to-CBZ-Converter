# /////////////////////////////////////////////////////////////////////////
# //                                                                     //
# //            Book 2 CBZ Converter by KenWeTech                        //
# //                 Part 2: create cbz(s)                               //
# //                                                                     //
# /////////////////////////////////////////////////////////////////////////

import os
import sys
import shutil
import subprocess
import zipfile
import xml.etree.ElementTree as ET
import json
import re
import tempfile
from PIL import Image
import fitz  # PyMuPDF
from PyPDF2 import PdfReader
import numpy as np

# --- Input Directory Setup ---
# Define input directory.
# Replace this with the path to the folder containing your books (PDFs).
# Example:input_dir = r'C:\Users\YourName\Documents\Books'
# If you are unsure where your books are, you can place this script in the same folder as your books.
# Then, you can change the input_dir to the current directory with: os.getcwd()
input_dir = os.getcwd()  # Default to current directory. Change if needed.

# --- Configuration Flags ---
# Flags to control file deletions and features
delete_pdf = True  # Set to True to delete the original PDF after processing. False keeps it.
delete_json = True  # Set to True to delete the JSON files after processing. False keeps it.
crop_white_margins_enabled = True  # Set to True to crop white margins from images. False skips cropping.
create_comicinfo_enabled = True  # Set to True to create a ComicInfo.xml file. False skips it.
chapter_page_filter_threshold = 8  # Threshold for filtering chapter pages if 'chapter 2' in toc is not found.
min_chapters_for_split = 3  # Minimum number of chapters to trigger chapter splitting.
overwrite_existing_cbz = True # Set to True to overwrite existing cbz files. False skips if it exist
remove_prefix_cbz = True  # Flag to control 'V ' prefix removal for CBZ

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

# --- Function: Path Structure ---
def create_output_structure(input_path):
    """Creates the output directory structure for processed files."""
    return os.path.dirname(input_path)

# --- Function: Read Chapter Information from JSON ---
def read_chapter_info(info_path):
    """Reads chapter information from a JSON file."""
    chapter_pages = []
    chapters_data = []

    if not os.path.exists(info_path):
        print_status(f"Chapter info file not found: {info_path}", "warn")
        return chapter_pages

    try:
        with open(info_path, 'r', encoding='utf-8') as f:
            chapters_data = json.load(f)

        if chapters_data:
            chapters_data.sort(key=lambda x: x['page'])

            chapter_two_found = False
            chapter_two_page = None
            chapter_two_index = -1
            for index, chapter in enumerate(chapters_data):
                if isinstance(chapter, dict) and 'title' in chapter and 'page' in chapter:
                    title = chapter['title'].lower()
                    if "chapter 2" in title or "two" == title or "chapter two" in title:
                        chapter_two_page = chapter['page']
                        chapter_two_found = True
                        chapter_two_index = index
                        break

            for chapter in chapters_data:
                if isinstance(chapter, dict) and 'page' in chapter:
                    chapter_pages.append(chapter['page'])

            chapter_pages = list(dict.fromkeys(chapter_pages))

            if chapter_two_found and chapter_two_index > 0:
                first_chapter_page = chapter_pages[0]
                filtered_chapter_pages = [page for page in chapter_pages[1:chapter_two_index] if page >= first_chapter_page + chapter_page_filter_threshold]
                chapter_pages = [first_chapter_page] + filtered_chapter_pages + chapter_pages[chapter_two_index:]
            else:
                if len(chapter_pages) > 1:
                    first_chapter_page = chapter_pages[0]
                    filtered_chapter_pages = [page for page in chapter_pages[1:] if page >= first_chapter_page + chapter_page_filter_threshold]
                    chapter_pages = [first_chapter_page] + filtered_chapter_pages

    except Exception as e:
        print_status(f"Error reading chapter info file {info_path}: {e}", "error")

    print_status(f"Chapter pages: {chapter_pages}", "info")
    return chapter_pages

# --- Function: Process Chapters ---
def process_chapters(pdf_path, info_path, output_folder, file_name, chapter_pages, opf_path):
    is_root_dir = os.path.dirname(pdf_path) == input_dir
    if is_root_dir:
        temp_dir = tempfile.mkdtemp(dir=output_folder)
        print_status(f"Created temporary directory: {temp_dir}", "info")
    else:
        temp_dir = output_folder

    if len(chapter_pages) > 0:
        print_status(f"Found {len(chapter_pages)} chapter breaks in the PDF.", "info")
        start_page = 1
        end_page = chapter_pages[0] - 1 if chapter_pages[0] > 1 else None
        print_status(f"Processing Chapter 1: pages {start_page}-{end_page}", "info")
        images_dir = os.path.join(temp_dir, "chapter_1")
        convert_pdf_to_images(pdf_path, images_dir, start_page, end_page)

        chapter_num = 1
        metadata_file = get_metadata_json(os.path.dirname(pdf_path))
        metadata = parse_metadata_json(metadata_file) if metadata_file else {}
        if create_comicinfo_enabled:
            print_status(f"Creating ComicInfo for chapter {chapter_num} with metadata: {metadata}", "info")
            comicinfo_path = create_comicinfo(metadata, chapter_num, temp_dir)
        else:
            comicinfo_path = None
        output_cbz = os.path.join(temp_dir, f"{os.path.splitext(file_name)[0]} Chapter {chapter_num}.cbz")
        create_cbz(images_dir, output_cbz, comicinfo_path)

        for i in range(1, len(chapter_pages)):
            start_page = chapter_pages[i - 1]
            if i < len(chapter_pages) - 1:
                end_page = chapter_pages[i] - 1
            else:
                end_page = None

            chapter_num = i + 1
            print_status(f"Processing Chapter {chapter_num}: pages {start_page}-{end_page}", "info")
            images_dir = os.path.join(temp_dir, f"chapter_{chapter_num}")
            convert_pdf_to_images(pdf_path, images_dir, start_page, end_page)

            metadata_file = get_metadata_json(os.path.dirname(pdf_path))
            metadata = parse_metadata_json(metadata_file) if metadata_file else {}
            if create_comicinfo_enabled:
                print_status(f"Creating ComicInfo for chapter {chapter_num} with metadata: {metadata}", "info")
                comicinfo_path = create_comicinfo(metadata, chapter_num, temp_dir)
            else:
                comicinfo_path = None
            output_cbz = os.path.join(temp_dir, f"{os.path.splitext(file_name)[0]} Chapter {chapter_num}.cbz")
            create_cbz(images_dir, output_cbz, comicinfo_path)

        cleanup(images_dir=temp_dir, pdf_path=pdf_path, comicinfo_path=comicinfo_path, json_path=info_path if os.path.exists(info_path) else None)

        if is_root_dir:
            shutil.rmtree(temp_dir)
            print_status(f"Cleaned up temporary directory: {temp_dir}", "info")
    else:
        print_status("No chapter breaks found in the PDF.", "warn")

# --- Function: Crop White Margins ---
def crop_white_margins(image_path, padding=10):
    if crop_white_margins_enabled:
        with Image.open(image_path) as img:
            grayscale_img = img.convert('L')
            img_array = np.array(grayscale_img)
            non_white_rows = np.any(img_array < 255, axis=1)
            non_white_cols = np.any(img_array < 255, axis=0)
            top = np.argmax(non_white_rows)
            bottom = len(non_white_rows) - np.argmax(non_white_rows[::-1]) - 1
            left = np.argmax(non_white_cols)
            right = len(non_white_cols) - np.argmax(non_white_cols[::-1]) - 1
            top = max(0, top - padding)
            bottom = min(img.height, bottom + padding)
            left = max(0, left - padding)
            right = min(img.width, right + padding)
            img_cropped = img.crop((left, top, right, bottom))
            img_cropped.save(image_path)
            print_status(f"Cropped white margins from: {image_path}", "info")
    else:
        print_status(f"Skipping cropping white margins for: {image_path}", "info")

# --- Function: Convert PDF to Images ---
def convert_pdf_to_images(pdf_path, images_dir, start_page, end_page):
    print_status(f"Converting PDF pages {start_page} to {end_page-1 if end_page else 'end'} to images...", "info")
    os.makedirs(images_dir, exist_ok=True)
    command = [
        "magick", "convert",
        "-background", "white", "-alpha", "remove",
        f"{pdf_path}[{start_page-1 if start_page > 0 else 0}-{end_page-2 if end_page and end_page > 1 else 'last'}]",
        "-gravity", "Center",
        "-extent", "100%x100%",
        os.path.join(images_dir, "image-%04d.webp")
    ]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print_status(f"Error running magick convert: {e}", "error")
    for image_file in sorted(os.listdir(images_dir)):
        image_path = os.path.join(images_dir, image_file)
        if image_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            crop_white_margins(image_path)

# --- Function: Create ComicInfo.xml ---
def create_comicinfo(metadata, chapter_num, output_dir):
    comicinfo = f"""<?xml version="1.0" encoding="UTF-8"?>
<ComicInfo>
    <Title>{metadata.get('title', '')}</Title>
    <LocalizedSeries>{metadata.get('localized_series', '')}</LocalizedSeries>
    <Series>{metadata.get('localized_series', '')}</Series>
    <Number>{chapter_num}</Number>
    <Count>{metadata.get('count', '')}</Count>
    <Volume>{metadata.get('number', '')}</Volume>
    <Summary>{metadata.get('summary', '')}</Summary>
    <Publisher>{metadata.get('publisher', '')}</Publisher>
    <Year></Year>
    <Month></Month>
    <Day></Day>
    <Writer>{metadata.get('writer', '')}</Writer>
    <Penciller>{metadata.get('penciller', '')}</Penciller>
    <Inker>{metadata.get('inker', '')}</Inker>
    <Colorist>{metadata.get('colorist', '')}</Colorist>
    <Letterer>{metadata.get('letterer', '')}</Letterer>
    <CoverArtist>{metadata.get('cover_artist', '')}</CoverArtist>
    <Editor>{metadata.get('editor', '')}</Editor>
    <Translator>{metadata.get('translator', '')}</Translator>
    <Genre>{metadata.get('genre', '')}</Genre>
    <Tags>{metadata.get('tags', '')}</Tags>
    <Web>{metadata.get('web', '')}</Web>
    <LanguageISO>{metadata.get('language', '')}</LanguageISO>
    <Format>{metadata.get('format', '')}</Format>
    <SeriesGroup>{metadata.get('localized_series', '')}</SeriesGroup>
    <AgeRating>{metadata.get('age_rating', '')}</AgeRating>
    <GTIN>{metadata.get('gtin', '')}</GTIN>
    <Status>{metadata.get('status', '')}</Status>
    <Price>{metadata.get('price', '')}</Price>
    <Country>{metadata.get('country', '')}</Country>
    <Barcode>{metadata.get('barcode', '')}</Barcode>
    <Imprint>{metadata.get('imprint', '')}</Imprint>
</ComicInfo>"""

    comicinfo_path = os.path.join(output_dir, 'ComicInfo.xml')
    with open(comicinfo_path, 'w', encoding='utf-8') as f:
        f.write(comicinfo)
    return comicinfo_path

# --- Function: Get Metadata JSON ---
def get_metadata_json(pdf_path):
    """Gets the metadata JSON file associated with the given PDF."""
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    metadata_filename = f"{pdf_name} metadata.json"
    metadata_path = os.path.join(os.path.dirname(pdf_path), metadata_filename)

    if os.path.exists(metadata_path):
        return metadata_path
    else:
        return None

# --- Function: Parse Metadata JSON ---
def parse_metadata_json(metadata_file):
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        return metadata
    except FileNotFoundError:
        print_status(f"Error: Metadata file not found: {metadata_file}", "error")
        return {}
    except json.JSONDecodeError as e:
        print_status(f"Error: Invalid JSON format in {metadata_file}: {e}", "error")
        return {}
    except UnicodeDecodeError as e:
        print_status(f"Error: Unicode decoding error in {metadata_file}: {e}", "error")
        return {}

# --- Function: Create CBZ Archive ---
def create_cbz(images_dir, output_cbz, comicinfo_path):
    if not overwrite_existing_cbz and os.path.exists(output_cbz):
        print_status(f"CBZ file already exists: {output_cbz}. Skipping creation.", "warn")
        return

    with zipfile.ZipFile(output_cbz, 'w', zipfile.ZIP_DEFLATED) as cbz:
        for image_file in sorted(os.listdir(images_dir)):
            cbz.write(os.path.join(images_dir, image_file), image_file)
        if comicinfo_path and os.path.exists(comicinfo_path):
            cbz.write(comicinfo_path, "ComicInfo.xml")
    print_status(f"Created CBZ archive: {output_cbz}", "success")

# --- Function: Cleanup ---
def cleanup(images_dir=None, pdf_path=None, comicinfo_path=None, json_path=None, metadata_path=None):
    if images_dir and os.path.exists(images_dir) and os.path.isdir(images_dir):
        shutil.rmtree(images_dir)
        print_status(f"Cleaned up image directory: {images_dir}", "info")
    if comicinfo_path and os.path.exists(comicinfo_path) and os.path.isfile(comicinfo_path):
        os.remove(comicinfo_path)
        print_status(f"Removed ComicInfo.xml: {comicinfo_path}", "info")

    try:
        if delete_json and metadata_path and os.path.exists(metadata_path):
            os.remove(metadata_path)
            print_status(f"Removed metadata: {metadata_path}", "info")
    except Exception as e:
        print_status(f"Error during metadata cleanup: {e}", "error")

    if delete_pdf and pdf_path and os.path.exists(pdf_path) and os.path.isfile(pdf_path):
        os.remove(pdf_path)
        print_status(f"Removed PDF: {pdf_path}", "info")

    if delete_json and json_path and os.path.exists(json_path):
        os.remove(json_path)
        print_status(f"Removed Chapter JSON: {json_path}", "info")

# --- Function: Cleanup CBZ Filename ---
def cleanup_cbz_filename(cbz_path):
    """Removes 'V ' from the beginning of a CBZ filename."""
    directory = os.path.dirname(cbz_path)
    filename = os.path.basename(cbz_path)
    if filename.startswith('V '):
        new_filename = filename[2:]
        new_path = os.path.join(directory, new_filename)
        try:
            os.rename(cbz_path, new_path)
            print_status(f"Renamed '{filename}' to '{new_filename}'", "info")
            return new_path
        except Exception as e:
            print_status(f"Error renaming '{filename}': {e}", "error")
            return cbz_path
    return cbz_path

# --- Main Function ---
def main():
    print_status(f"Starting the process with input directory: {input_dir}", "info")
    for folder_path, _, file_names in os.walk(input_dir):
        for file_name in file_names:
            if file_name.lower().endswith('.pdf'):
                pdf_path = os.path.join(folder_path, file_name)
                info_path = os.path.join(folder_path, os.path.splitext(file_name)[0] + ' chapters.json')
                output_folder = create_output_structure(pdf_path)

                if os.path.exists(info_path):
                    print_status(f"Reading chapter info from: {info_path}", "info")
                    chapter_pages = read_chapter_info(info_path)
                    if len(chapter_pages) >= min_chapters_for_split:
                        for i in range(len(chapter_pages) - 1):
                            start_page, end_page = chapter_pages[i], chapter_pages[i + 1]
                            images_dir = os.path.join(output_folder, f"chapter_{i+1}")
                            convert_pdf_to_images(pdf_path, images_dir, start_page, end_page)

                            # Fetch and parse metadata PER CHAPTER
                            metadata_file = get_metadata_json(pdf_path)
                            metadata = parse_metadata_json(metadata_file) if metadata_file else {}
                            if create_comicinfo_enabled:
                                if not sys.platform.startswith('win'):
                                    print_status(f"Creating ComicInfo for chapter {i + 1} with metadata: {metadata}", "info")
                                comicinfo_path = create_comicinfo(metadata, i + 1, output_folder)
                            else:
                                comicinfo_path = None
                            output_cbz = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]} Chapter {i+1}.cbz")
                            create_cbz(images_dir, output_cbz, comicinfo_path)
                            cleanup(images_dir)
                        cleanup(pdf_path=pdf_path, comicinfo_path=os.path.join(output_folder, 'ComicInfo.xml'), json_path=info_path if os.path.exists(info_path) else None, metadata_path=get_metadata_json(pdf_path))
                    else:
                        images_dir = os.path.join(output_folder, "whole_pdf")
                        os.makedirs(images_dir, exist_ok=True)
                        convert_pdf_to_images(pdf_path, images_dir, 0, 9999)

                        # Fetch and parse metadata for the whole PDF
                        metadata_file = get_metadata_json(pdf_path)
                        metadata = parse_metadata_json(metadata_file) if metadata_file else {}
                        if create_comicinfo_enabled:
                            if not sys.platform.startswith('win'):
                                print_status(f"Creating ComicInfo for whole PDF with metadata: {metadata}", "info")
                            comicinfo_path = create_comicinfo(metadata, 1, output_folder) # Assuming single CBZ for whole PDF
                        else:
                            comicinfo_path = None
                        output_cbz = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}.cbz")
                        create_cbz(images_dir, output_cbz, comicinfo_path)
                        cleanup(images_dir)
                        cleanup(pdf_path=pdf_path, comicinfo_path=os.path.join(output_folder, 'ComicInfo.xml'), json_path=info_path if os.path.exists(info_path) else None, metadata_path=get_metadata_json(pdf_path))
                else:
                    print_status(f"No chapter info found. Converting entire PDF to CBZ: {pdf_path}", "warn")
                    images_dir = os.path.join(output_folder, "whole_pdf")
                    os.makedirs(images_dir, exist_ok=True)
                    convert_pdf_to_images(pdf_path, images_dir, 0, 9999)

                    # Fetch and parse metadata for the whole PDF
                    metadata_file = get_metadata_json(pdf_path)
                    metadata = parse_metadata_json(metadata_file) if metadata_file else {}
                    if create_comicinfo_enabled:
                        if not sys.platform.startswith('win'):
                            print_status(f"Creating ComicInfo for whole PDF with metadata: {metadata}", "info")
                        comicinfo_path = create_comicinfo(metadata, 1, output_folder) # Assuming single CBZ for whole PDF
                    else:
                        comicinfo_path = None
                    output_cbz = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}.cbz")
                    create_cbz(images_dir, output_cbz, comicinfo_path)
                    cleanup(images_dir)
                    cleanup(pdf_path=pdf_path, comicinfo_path=os.path.join(output_folder, 'ComicInfo.xml'), json_path=None, metadata_path=get_metadata_json(pdf_path))

                if os.path.dirname(pdf_path) == input_dir:
                    shutil.rmtree(output_folder)
                    print_status(f"Cleaned up temporary directory: {output_folder}", "info")
                if delete_pdf and pdf_path and os.path.exists(pdf_path) and os.path.isfile(pdf_path):
                    os.remove(pdf_path)
                    print_status(f"Removed PDF: {pdf_path}", "info")

if __name__ == "__main__":
    main()

    if remove_prefix_cbz:
        print_status("Scanning for CBZ files to clean...", "info")
        for folder_path, _, file_names in os.walk(input_dir):
            for file_name in file_names:
                if file_name.lower().endswith('.cbz') and file_name.startswith("V "):
                    cbz_path = os.path.join(folder_path, file_name)
                    cleanup_cbz_filename(cbz_path)
        print_status("CBZ filename cleanup complete.", "success")
