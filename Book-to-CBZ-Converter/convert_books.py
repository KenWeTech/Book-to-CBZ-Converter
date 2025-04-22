# /////////////////////////////////////////////////////////////////////////
# //                                                                     //
# //            Book 2 CBZ Converter by KenWeTech                        //
# //                                                                     //
# /////////////////////////////////////////////////////////////////////////

# =============================================================
# =        Don't Make Any Changes Here                        =
# =============================================================

import os
import sys
import subprocess
import datetime
import time
import shutil

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

print_status("Starting book conversion...", "info")
print()

def run_python_script(script_name, target_folder):
    log_file_name = f"error_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    log_file_path = os.path.join(target_folder, log_file_name)
    try:
        print_status(f"Running {script_name} in {target_folder}...", "info")
        process = subprocess.run(
            [sys.executable, script_name, target_folder],
            check=True,  # Raise an exception for non-zero exit codes
            capture_output=True,
            text=True
        )
        print_status(f"{script_name} completed successfully.", "success")
    except subprocess.CalledProcessError as e:
        print_status(f"Error occurred during {script_name}:", "error")
        print(f"Return Code: {e.returncode}")
        print(f"Stdout:\n{e.stdout}")
        print(f"Stderr:\n{e.stderr}")
        with open(log_file_path, "w") as f:
            f.write(f"Error during {script_name} at {datetime.datetime.now()}\n")
            f.write(f"Return Code: {e.returncode}\n")
            f.write(f"Stdout:\n{e.stdout}\n")
            f.write(f"Stderr:\n{e.stderr}\n")
        print_status(f"Error details saved to: {log_file_path}", "warn")
        sys.exit(1)
    except FileNotFoundError:
        print_status(f"Error: Python script '{script_name}' not found in the current directory.", "error")
        sys.exit(1)
    except Exception as e:
        print_status(f"An unexpected error occurred: {e}", "error")
        sys.exit(1)

if __name__ == "__main__":
    target_folder = os.getcwd()
    print_status(f"Target folder set to current directory: {target_folder}", "info")

    run_python_script("p1_process_books.py", target_folder)
    run_python_script("p2_create_cbz.py", target_folder)

    print_status("All tasks completed!", "success")

if os.path.exists("__pycache__"):
    shutil.rmtree("__pycache__")

    time.sleep(5)

