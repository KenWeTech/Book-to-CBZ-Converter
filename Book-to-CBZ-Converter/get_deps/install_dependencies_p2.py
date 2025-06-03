# =============================================================
# =         Installation of Dependencies: Part 2              =
# =============================================================

# =============================================================
# =             Don't Make Any Changes Here                   =
# =============================================================

import subprocess
import sys
import os
import importlib.util

def is_installed(module_name):
    """Checks if a Python module is installed."""
    return importlib.util.find_spec(module_name) is not None

def is_magick_installed():
    """Checks if ImageMagick's 'magick' command is installed."""
    try:
        subprocess.check_output(['magick', '--version'], stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def is_ghostscript_installed():
    """Checks if Ghostscript's 'gs' command is installed."""
    command = 'gswin64c' if sys.platform.startswith('win') else 'gs'
    try:
        subprocess.check_output([command, '--version'], stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        # On Windows, gs might be named gs.exe directly in path for some installations
        if sys.platform.startswith('win'):
            try:
                subprocess.check_output(['gs', '--version'], stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
                return True
            except (FileNotFoundError, subprocess.CalledProcessError):
                return False
        return False


def is_chocolatey_installed():
    """Checks if Chocolatey's 'choco' command is installed (Windows only)."""
    if not sys.platform.startswith('win'):
        return False
    try:
        subprocess.check_output(['choco', '--version'], stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def install_dependencies():
    """Installs required Python packages, ImageMagick, and Ghostscript."""
    try:
        # Install Python packages
        python_deps = ['Pillow', 'PyMuPDF', 'PyPDF2', 'numpy', 'ebooklib'] # PyMuPDF is 'fitz'
        missing_python_deps = [dep for dep in python_deps if not is_installed(dep)]

        if missing_python_deps:
            print(f"Attempting to install missing Python dependencies: {', '.join(missing_python_deps)}")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_python_deps)
            print(f"Installed Python dependencies: {', '.join(missing_python_deps)}")
        else:
            print("All required Python dependencies are already installed.")

        # Install ImageMagick
        print("\n--- Checking ImageMagick ---")
        if sys.platform.startswith('win'):
            if not is_magick_installed():
                print("ImageMagick not found.")
                try:
                    # Check if winget is available
                    subprocess.check_call(['winget', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print("Attempting to install ImageMagick using winget...")
                    # Install ImageMagick using winget
                    subprocess.check_call(['winget', 'install', '--id', 'ImageMagick.ImageMagick', '--silent', '--accept-source-agreements'])
                    print("ImageMagick installed successfully via winget.")

                    # Add ImageMagick to PATH (this may not always be necessary, winget often does it)
                    magick_path = r"C:\Program Files\ImageMagick-7.1.16-Q16-HDRI" # Default ImageMagick Path. May change with new versions.
                    os.environ['PATH'] += os.pathsep + magick_path
                    print("ImageMagick Path added to environment variables.")

                except FileNotFoundError:
                    print("winget not found. Please install winget or ImageMagick manually.")
                except subprocess.CalledProcessError as e:
                    print(f"Error installing ImageMagick via winget: {e}")
            else:
                print("ImageMagick is already installed.")

        elif sys.platform.startswith('linux'):
            if not is_magick_installed():
                print("ImageMagick not found. Attempting to install using apt-get...")
                try:
                    # Install ImageMagick on Linux (Debian/Ubuntu)
                    print("Updating package list (sudo required)...")
                    subprocess.check_call(['sudo', 'apt-get', 'update'])
                    print("Installing imagemagick (sudo required)...")
                    subprocess.check_call(['sudo', 'apt-get', 'install', '-y', 'imagemagick'])
                    print("ImageMagick installed successfully on Linux.")
                except subprocess.CalledProcessError as e:
                    print(f"Error installing ImageMagick on Linux: {e}")
            else:
                print("ImageMagick is already installed.")

        elif sys.platform.startswith('darwin'):
            if not is_magick_installed():
                print("ImageMagick not found. Attempting to install using Homebrew...")
                try:
                    # Install ImageMagick on macOS using Homebrew
                    subprocess.check_call(['brew', 'install', 'imagemagick'])
                    print("ImageMagick installed successfully on macOS.")
                except FileNotFoundError:
                    print("Homebrew not found. Please install Homebrew (see https://brew.sh/) and then ImageMagick ('brew install imagemagick').")
                except subprocess.CalledProcessError as e:
                    print(f"Error installing ImageMagick on macOS: {e}")
            else:
                print("ImageMagick is already installed.")

        # Install Ghostscript
        print("\n--- Checking Ghostscript ---")
        if not is_ghostscript_installed():
            print("Ghostscript not found.")
            if sys.platform.startswith('win'):
                # Windows: Ghostscript installation using Chocolatey
                choco_available = is_chocolatey_installed()
                if not choco_available:
                    print("Chocolatey (choco) is not installed. It's recommended for installing Ghostscript on Windows.")
                    choice = input("Would you like to: \n"
                                   "  1. Attempt to install Chocolatey automatically using winget (recommended)?\n"
                                   "  2. Install Chocolatey manually from https://chocolatey.org/install and then continue?\n"
                                   "  3. Skip Ghostscript installation?\n"
                                   "Enter your choice (1, 2, or 3): ").strip()
                    if choice == '1':
                        try:
                            print("Attempting to install Chocolatey using winget...")
                            subprocess.check_call(['winget', 'install', '--id', 'Chocolatey.Chocolatey', '-e', '--source', 'winget', '--accept-package-agreements', '--accept-source-agreements', '--silent'])
                            print("Chocolatey installation via winget initiated.")
                            input("Press Enter to continue. After pressing Enter, a new window will open to install Ghostscript using Chocolatey. Please ensure Chocolatey is fully set up (a system restart or new terminal might be needed for 'choco' to be universally available if issues arise).")
                            choco_available = True # Assume it will be available for the new window
                        except FileNotFoundError:
                            print("Winget not found. Cannot install Chocolatey automatically. Please install Chocolatey manually or skip Ghostscript.")
                        except subprocess.CalledProcessError as e:
                            print(f"Error installing Chocolatey via winget: {e}. Please install Chocolatey manually or skip Ghostscript.")
                    elif choice == '2':
                        print("Please install Chocolatey from https://chocolatey.org/install")
                        input("Once Chocolatey is installed and available (you might need to open a new terminal/Command Prompt for 'choco' to be recognized), press Enter here to continue with Ghostscript installation.")
                        choco_available = True # Assume user installed it
                    else:
                        print("Ghostscript installation skipped by user.")

                if choco_available or is_chocolatey_installed(): # Re-check in case it was installed manually and PATH updated
                    if not is_chocolatey_installed(): # Final check if user said they installed it but it's not found
                        print("Chocolatey command 'choco' not found even after attempting installation/manual setup. Cannot install Ghostscript.")
                    else:
                        print("Attempting to install Ghostscript using Chocolatey in a NEW window.")
                        gs_install_command = "choco install ghostscript -y --force" # --force to handle potential re-installs
                        launch_command = f'cmd /c start cmd /k "{gs_install_command} && echo --- Ghostscript installation process has finished. You can type exit and press Enter to close this window. --- && pause"'
                        try:
                            subprocess.Popen(launch_command, shell=True)
                            print(f"\nA new command window has been opened to execute: {gs_install_command}")
                            input("==> IMPORTANT: Please monitor the new window. Once Ghostscript installation is complete there, close that window (or type 'exit' and press Enter), and then press Enter in THIS window to continue script execution. <==")
                            if is_ghostscript_installed():
                                print("Ghostscript appears to be installed now.")
                            else:
                                print("Ghostscript might not have installed correctly or is not yet in PATH. Please verify manually.")
                        except Exception as e:
                            print(f"Failed to launch new window for Ghostscript installation: {e}")
                            print(f"You can try running this command manually in a new Administrator Command Prompt: {gs_install_command}")
                else:
                    if choice not in ['1','2','3']: # If invalid choice was made earlier
                        print("Invalid choice for Chocolatey installation. Ghostscript installation skipped.")
                    # If choco wasn't available and user didn't choose to install it or installation failed
                    elif choice == '3':
                        pass # Already handled: "Ghostscript installation skipped by user."
                    else:
                         print("Chocolatey not available, Ghostscript installation on Windows will be skipped. Some functionalities may be affected.")


            elif sys.platform.startswith('linux'):
                # Install Ghostscript on Linux (Debian/Ubuntu)
                print("Attempting to install Ghostscript using apt-get...")
                try:
                    print("Updating package list (sudo required)...")
                    subprocess.check_call(['sudo', 'apt-get', 'update'])
                    print("Installing ghostscript (sudo required)...")
                    subprocess.check_call(['sudo', 'apt-get', 'install', '-y', 'ghostscript'])
                    print("Ghostscript installed successfully on Linux.")
                except subprocess.CalledProcessError as e:
                    print(f"Error installing Ghostscript on Linux: {e}")
            elif sys.platform.startswith('darwin'):
                # Install Ghostscript on macOS using Homebrew
                print("Attempting to install Ghostscript using Homebrew...")
                try:
                    subprocess.check_call(['brew', 'install', 'ghostscript'])
                    print("Ghostscript installed successfully on macOS.")
                except FileNotFoundError:
                    print("Homebrew not found. Please install Homebrew (see https://brew.sh/) and then Ghostscript ('brew install ghostscript').")
                except subprocess.CalledProcessError as e:
                    print(f"Error installing Ghostscript on macOS via Homebrew: {e}")
            else:
                print(f"Ghostscript installation not configured for this platform: {sys.platform}")
        else:
            print("Ghostscript is already installed.")

    except subprocess.CalledProcessError as e:
        print(f"Error during installation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_dependencies()
    print("If any new command-line tools were installed (like ImageMagick, Ghostscript, or Chocolatey),")
    print("you might need to restart your terminal/Command Prompt or even your system for them to be fully available in your PATH.")
