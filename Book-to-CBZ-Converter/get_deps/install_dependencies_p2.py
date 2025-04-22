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
        subprocess.check_output(['magick', '--version'], stderr=subprocess.DEVNULL)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def install_dependencies():
    """Installs required Python packages and ImageMagick (Windows/Linux)."""
    try:
        # Install Python packages
        python_deps = ['Pillow', 'fitz', 'PyPDF2', 'numpy', 'ebooklib']
        missing_python_deps = [dep for dep in python_deps if not is_installed(dep)]

        if missing_python_deps:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_python_deps)
            print(f"Installed Python dependencies: {', '.join(missing_python_deps)}")
        else:
            print("All required Python dependencies are already installed.")

        # Install ImageMagick
        if sys.platform.startswith('win'):
            if not is_magick_installed():
                try:
                    # Check if winget is available
                    subprocess.check_call(['winget', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

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
                try:
                    # Install ImageMagick on Linux (Debian/Ubuntu)
                    subprocess.check_call(['sudo', 'apt-get', 'update'])
                    subprocess.check_call(['sudo', 'apt-get', 'install', '-y', 'imagemagick'])
                    print("ImageMagick installed successfully on Linux.")
                except subprocess.CalledProcessError as e:
                    print(f"Error installing ImageMagick on Linux: {e}")
            else:
                print("ImageMagick is already installed.")

        elif sys.platform.startswith('darwin'):
            if not is_magick_installed():
                try:
                    # Install ImageMagick on macOS using Homebrew
                    subprocess.check_call(['brew', 'install', 'imagemagick'])
                    print("ImageMagick installed successfully on macOS.")
                except subprocess.CalledProcessError as e:
                    print(f"Error installing ImageMagick on macOS: {e}")
            else:
                print("ImageMagick is already installed.")

    except subprocess.CalledProcessError as e:
        print(f"Error during installation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_dependencies()