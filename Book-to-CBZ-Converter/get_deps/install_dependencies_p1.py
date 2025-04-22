# =============================================================
# =         Installation of Dependencies: Part 1              =
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

def is_calibre_installed():
    """Checks if Calibre's ebook-convert is installed."""
    try:
        subprocess.check_output(['ebook-convert', '--version'], stderr=subprocess.DEVNULL)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def install_dependencies():
    """Installs required Python packages and Calibre (Windows/Linux/macOS)."""
    try:
        # Install Python packages
        python_deps = ['PyPDF2', 'ebooklib', 'beautifulsoup4']
        missing_python_deps = [dep for dep in python_deps if not is_installed(dep)]

        if missing_python_deps:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_python_deps)
            print(f"Installed Python dependencies: {', '.join(missing_python_deps)}")
        else:
            print("All required Python dependencies are already installed.")

        # Install Calibre
        if sys.platform.startswith('win'):
            if not is_calibre_installed():
                try:
                    # Check if winget is available
                    subprocess.check_call(['winget', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                    # Install Calibre using winget
                    subprocess.check_call(['winget', 'install', '--id=calibre.calibre', '-e', '--silent', '--accept-source-agreements'])
                    print("Calibre installed successfully via winget.")

                    # Add Calibre to PATH (this may not always be necessary, winget often does it)
                    calibre_path = r"C:\Program Files\Calibre2" # Default Calibre Path.
                    os.environ['PATH'] += os.pathsep + calibre_path
                    print("Calibre Path added to environment variables.")

                except FileNotFoundError:
                    print("winget not found. Please install winget or Calibre manually.")
                except subprocess.CalledProcessError as e:
                    print(f"Error installing Calibre via winget: {e}")
            else:
                print("Calibre is already installed.")

        elif sys.platform.startswith('linux'):
            if not is_calibre_installed():
                try:
                    # Install Calibre on Linux
                    subprocess.check_call(['sudo', '-v']) # Check sudo before running long command.
                    subprocess.check_call(['wget', '-nv', '-O-', 'https://download.calibre-ebook.com/linux-installer.sh'], stdout=subprocess.PIPE)
                    subprocess.check_call(['sudo', 'sh', '/dev/stdin'], input=subprocess.check_output(['wget', '-nv', '-O-', 'https://download.calibre-ebook.com/linux-installer.sh']))
                    print("Calibre installed successfully on Linux.")
                except subprocess.CalledProcessError as e:
                    print(f"Error installing Calibre on Linux: {e}")
            else:
                print("Calibre is already installed.")

        elif sys.platform.startswith('darwin'):
            if not is_calibre_installed():
                try:
                    # Install Calibre on macOS using brew cask
                    subprocess.check_call(['brew', 'install', '--cask', 'calibre'])
                    print("Calibre installed successfully on macOS via brew cask.")
                except subprocess.CalledProcessError as e:
                    print(f"Error installing Calibre on macOS: {e}")
            else:
                print("Calibre is already installed.")

    except subprocess.CalledProcessError as e:
        print(f"Error during installation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_dependencies()