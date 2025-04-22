# ######################################################################################
# #                                                                                    #
# #        Interactive Configuration for Book Conversion by KenWeTech                  #
# #                                                                                    #
# ######################################################################################

# =============================================================
# =             Don't Make Any Changes Here                   =
# =============================================================

import re
import os
import time

# Configuration mapping: script -> { flag_name: (type, prompt, default) }
CONFIG_FLAGS = {
    'p1_process_books.py': {
        'delete_epub': (bool, "Delete EPUB files? (set to false if this is in your calibre library) (True/False)", True),
        'delete_opf': (bool, "Delete OPF files? (set to false if this is in your calibre library) (True/False)", True),
        'add_first_page': (bool, "Add 'First Page' to TOC? (neccessary for chapter splitting when keeping cover page) (True/False)", True),
        'run_organize_epub': (bool, "Organize root files into subfolders? (neccessary for chapter splitting) (True/False)", True),
        'run_extract_toc': (bool, "Extract TOC from files that are available? (neccessary for chapter splitting) (True/False)", True),
        'font_size': (int, "Font size of text in the converted book(default size is great for small screens) (integer)", 30),
    },
    'p2_create_cbz.py': {
        'delete_pdf': (bool, "Delete PDF files after processing? (set to false if this is in your calibre library and you want to keep this format) (True/False)", True),
        'delete_json': (bool, "Delete JSON files after processing? (chapters and metadata files that were created for conversion) (True/False)", True),
        'crop_white_margins_enabled': (bool, "Crop white margins from pages? (reduces the empty white space thats not text, optional but True is recommended) (True/False)", False),
        'create_comicinfo_enabled': (bool, "Create ComicInfo.xml file for keeping metadata? (Set FALSE for file structure naming convention in Kavita for example) (True/False)", True),
        'chapter_page_filter_threshold': (int, "Chapter page filter threshold: (number of pages to still be considered chapter 1) (integer)", 8),
        'min_chapters_for_split': (int, "Minimum chapters needed to split CBZ Book into chapters, set to 9999 to make a single CBZ for book. (integer)", 3),
        'overwrite_existing_cbz': (bool, "Overwrite existing CBZ files? (True/False)", True),
        'remove_prefix_cbz': (bool, "Remove 'V ' prefix from CBZ files? (neccessary clean up for file structure naming convention setting) (True/False)", True),
    }
}

def parse_input(prompt, expected_type, current_value, default_value):
    while True:
        suffix = f" [current: {current_value}, default: {default_value}]"
        raw = input(f"{prompt}{suffix} (leave blank to use default): ").strip()
        if not raw:
            return default_value
        if expected_type is bool:
            if raw.lower() in ['true', 't', 'yes', 'y']:
                return True
            if raw.lower() in ['false', 'f', 'no', 'n']:
                return False
        elif expected_type is int:
            if raw.isdigit():
                return int(raw)
        print("Invalid input. Try again. Acceptable: True/False, T/F, Yes/No, Y/N for booleans, or an integer.")

def read_current_flags(script_path, flag_defs):
    current_flags = {}
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        for flag_name in flag_defs:  # Iterate through flag names in flag_defs
            match = re.search(rf"{flag_name}\s*=\s*(True|False|\d+)", content)
            if match:
                value = match.group(1)
                if value in ['True', 'False']:
                    current_flags[flag_name] = value == 'True'
                else:
                    current_flags[flag_name] = int(value)
            else:
                current_flags[flag_name] = flag_defs[flag_name][2]  # fallback to default
    except FileNotFoundError:
        print(f"[ERROR] File not found: {script_path}")
        for flag_name in flag_defs:
            current_flags[flag_name] = flag_defs[flag_name][2]  # fallback to default
    return current_flags

def get_current_directory(script_path):
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith("input_dir") and not line.startswith("#"):
                    match = re.search(r"input_dir\s*=\s*\s*(?:r?['\"])(.*?)(?:['\"])", line)
                    if match:
                        return match.group(1)
                    else:
                        match_no_quotes = re.search(r"input_dir\s*=\s*\s*(\S+)", line)
                        if match_no_quotes:
                            return match_no_quotes.group(1)
                        else:
                            return "os.getcwd()"
            return "os.getcwd()"  # If no active input_dir is found
    except FileNotFoundError:
        return "os.getcwd()"

def update_directory(script_path, new_directory):
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()

        pattern = r"(input_dir\s*=\s*)(.*)"
        replacement = r"\1r'{}'".format(new_directory.replace('\\', '\\\\')) # Escape backslashes for raw string
        updated_content, count = re.subn(pattern, replacement, content)

        if count > 0:
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"✅ Updated input directory in {os.path.basename(script_path)} to: {new_directory}")
            return new_directory  # Return the updated directory
        else:
            print(f"[WARN] Could not find 'input_dir' definition in {os.path.basename(script_path)}. Skipped.")
            return None
    except FileNotFoundError:
        print(f"[ERROR] File not found: {script_path}")
        return None

def update_flags_in_script(script_path, flags):
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    updated_content = content
    update_summary = {}

    for flag, value in flags.items():
        escaped_flag = re.escape(flag)
        pattern_str = r"({}\s*=\s*)(True|False|\d+)".format(escaped_flag)
        pattern = re.compile(pattern_str)
        match = pattern.search(updated_content)
        if match:
            replacement = f"{match.group(1)}{value}"
            updated_content = updated_content.replace(match.group(0), replacement, 1)
            update_summary[flag] = 1
        else:
            print(f"[WARN] Could not find flag '{flag}' in {script_path}. Skipped.")

    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    print(f"✅ Attempted to update {os.path.basename(script_path)}")
    return flags

def verify_changes(script_path, intended_flags, original_flag_defs):
    verified_flags = {}
    current_flags = read_current_flags(script_path, original_flag_defs)
    for flag, intended_value in intended_flags.items():
        actual_value = current_flags.get(flag)
        verified_flags[flag] = (intended_value, actual_value, intended_value == actual_value)
    return verified_flags

def main():
    print("\n🔧 Convert Books Configuration Console by KenWeTech\n")

    update_choice = input("Which script(s) do you want to configure? (p1, p2, or leave blank for both): ").strip().lower()

    scripts_to_configure = []
    if not update_choice or update_choice == 'both':
        scripts_to_configure = ['p1_process_books.py', 'p2_create_cbz.py']
    elif update_choice == 'p1':
        scripts_to_configure = ['p1_process_books.py']
    elif update_choice == 'p2':
        scripts_to_configure = ['p2_create_cbz.py']
    else:
        print("Invalid choice. Configuring both scripts.")
        scripts_to_configure = ['p1_process_books.py', 'p2_create_cbz.py']

    updated_directories = {}
    update_directories_choice = input(f"Do you want to update the book directory in the selected script(s)? (yes/no, default: no): ").strip().lower()

    if update_directories_choice in ['yes', 'y']:
        for script in scripts_to_configure:
            current_dir = get_current_directory(script)
            default_dir_meaning = "sets scanning to the directory of the scripts location"
            print(f"\n--- Configure '{script}' Directory ---")
            print(f"  Current input directory: {current_dir}")
            print(f"  Default input directory: os.getcwd() ({default_dir_meaning})")
            new_book_directory = input("Enter the new book directory path (leave blank to use default): ").strip()
            if new_book_directory:
                updated_dir = update_directory(script, new_book_directory)
                if updated_dir:
                    updated_directories[script] = updated_dir
            else:
                print(f"Using default input directory for {os.path.basename(script)}.")
                updated_directories[script] = os.getcwd()  # Store the actual default
        print()

    all_verified_flags = {}
    for script in scripts_to_configure:
        if script in CONFIG_FLAGS:
            flag_defs = CONFIG_FLAGS[script]
            print(f"\n--- Configure {script} Flags ---")
            current_values = read_current_flags(script, flag_defs)
            flag_values = {}
            for flag_name, (flag_type, prompt, default_value) in flag_defs.items():
                current_value = current_values.get(flag_name, default_value)
                flag_values[flag_name] = parse_input(prompt, flag_type, current_value, default_value)
            update_flags_in_script(script, flag_values)
            verified_flags = verify_changes(script, flag_values, flag_defs)
            all_verified_flags[script] = verified_flags
            print()
        else:
            print(f"[ERROR] Configuration not found for script: {script}")

    print("\n📝 Configuration Summary:")
    for script in scripts_to_configure:
        print(f"\n--- {script} ---")
        if script in updated_directories:
            input_dir_status = f"Input Directory: '{updated_directories[script]}'"
            print(f"  {input_dir_status}")
        if script in all_verified_flags:
            for flag, (intended, actual, success) in all_verified_flags[script].items():
                status = "✅ Success" if success else "❌ Failure"
                print(f"  - {flag}: Intended '{intended}', Actual '{actual}' - {status}")

    print("\n⏳ Waiting for 20 seconds to allow reading the summary...")
    time.sleep(20)
    print("Done.")

if __name__ == '__main__':
    main()
