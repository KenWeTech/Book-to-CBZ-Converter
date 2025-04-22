# =============================================================
# =        Interactive Installation of Dependencies           =
# =============================================================

# =============================================================
# =            Don't Make Any Changes Here                    =
# =============================================================

import os
import sys
import datetime
import subprocess

def is_windows():
    return sys.platform.startswith('win')

def is_tool_installed(tool_name):
    """Checks if a command-line tool is installed."""
    try:
        subprocess.run([tool_name, '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def display_main_menu():
    print("=" * 70)
    print("  Let's get your books ready for conversion!")
    print("  But first, we need to make sure the necessary components can run.")
    print("=" * 70)
    print("\nPlease select an action:")
    print("\n  1. Run BOTH dependency scripts (install_dependencies_p1.py and install_dependencies_p2.py)")
    print("  2. Run ONLY the first dependency script (install_dependencies_p1.py)")
    print("  3. Run ONLY the second dependency script (install_dependencies_p2.py)")
    print("  4. Exit the script")
    print()

def run_python_script(script_name, target_folder, log_file):
    print("-" * 60)
    print(f"Starting {script_name} ...")
    print("-" * 60)
    try:
        command = [sys.executable, script_name, target_folder]
        with open(log_file, "a") as f:
            process = subprocess.Popen(command, stdout=f, stderr=subprocess.STDOUT)
            process.wait()
        if process.returncode == 0:
            print(f"\n{script_name} completed successfully.")
            return True
        else:
            print(f"\nERROR: {script_name} encountered an error (exit code: {process.returncode}).")
            print(f"Please check the log file ({log_file}) for details.")
            return False
    except FileNotFoundError:
        print(f"\nERROR: Could not find the Python script: {script_name}")
        return False
    except Exception as e:
        print(f"\nAn unexpected error occurred while running {script_name}: {e}")
        return False

def check_and_install_dependencies():
    if is_windows():
        if not is_tool_installed('winget'):
            print("=" * 70)
            print("  WARNING: Winget is NOT installed.")
            print("  The dependency scripts might use Winget to install additional components.")
            print("  If you encounter errors during script execution, it might be due to missing dependencies")
            print("  that Winget would have installed.")
            print("  Winget can be obtained from the Microsoft Store or GitHub (https://github.com/microsoft/winget-cli).")
            print("=" * 70)
            input("Press Enter to continue anyway...\n")
        else:
            print("Winget is installed.")
            print("Continuing with script...")
    else:
        input("Press Enter to continue...\n")

def handle_post_script_options():
    print("\nWhat would you like to do next?")
    print("\n  1. Continue to the next script")
    print("  2. Save log to file (already saved)")
    print("  3. Retry the previous script")
    print("  4. Return to the main menu")
    print()
    while True:
        choice = input("Enter your choice (1-4): ")
        if choice in ["1", "2", "3", "4"]:
            return choice
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

def handle_final_options(log_file):
    print("\nWhat would you like to do now?")
    print("\n  1. Exit the script")
    print("  2. Save log to file (already saved)")
    print("  3. Retry the previous action")
    print("  4. Return to the main menu")
    print()
    while True:
        choice = input("Enter your choice (1-4): ")
        if choice in ["1", "2", "3", "4"]:
            return choice
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    target_folder = os.getcwd()
    print(f"Target folder set to current directory: {target_folder}\n")

    check_and_install_dependencies()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file_name = f"script_log_{timestamp}.txt"
    log_file_path = os.path.join(target_folder, log_file_name)

    while True:
        display_main_menu()
        choice = input("Enter your choice (1-4): ")

        if choice == "1": # Run both
            script1_success = run_python_script("install_dependencies_p1.py", target_folder, log_file_path)
            if script1_success:
                post_choice = handle_post_script_options()
                if post_choice == "1":
                    run_python_script("install_dependencies_p2.py", target_folder, log_file_path)
                elif post_choice == "3":
                    continue # Retry runBoth
                elif post_choice == "4":
                    continue # Return to main menu
            # If script1 failed, will go to final options

        elif choice == "2": # Run only script 1
            run_python_script("install_dependencies_p1.py", target_folder, log_file_path)

        elif choice == "3": # Run only script 2
            run_python_script("install_dependencies_p2.py", target_folder, log_file_path)

        elif choice == "4":
            print("\nExiting...")
            break

        else:
            print("Invalid choice.")
            continue

        final_choice = handle_final_options(log_file_path)
        if final_choice == "1":
            print("\nExiting...")
            break
        elif final_choice == "3":
            continue # Go back to the main menu to retry
        elif final_choice == "4":
            continue # Go back to the main menu