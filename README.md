# Book-to-CBZ-Converter

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://opensource.org/licenses/MIT)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Have you ever noticed that CBZ converters out there only extract images, losing the actual text from the book?** This converter solves that! It processes your **ePUB** and **PDF** eBooks, ensuring the text content is preserved as images within the comic book-friendly **CBZ** format. Enjoy reading your digital book collection like a true comic or manga on popular apps like **Paperback** (iOS) across all your devices. Plus, it retains your book's metadata if you choose, for a complete and organized reading experience.

## Key Features

* **Effortless eBook to CBZ Conversion:** Easily transform your ePUB and PDF files into the comic book-friendly CBZ format **while preserving the text as images**.
* **Read Anywhere:** Enjoy your converted books on popular comic book reader apps like Paperback (iOS) across all your devices.
* **Optimized for eBooks:** Intelligently handles metadata from your eBooks to provide a better reading experience.
* **Flexible Output:** Create a single CBZ file or split it into chapter-based files for easier navigation.
* **Cross-Platform Compatibility:** Works seamlessly on Windows, Linux, and macOS.
* **Simple Setup:** Includes helpful scripts to guide you through the installation of necessary tools.
* **Customizable Conversion:** Offers options to adjust font size, image quality, maximum image dimensions, and more.
* **Intelligent Image Handling:** Extracts and optimizes images from your eBooks for the CBZ format.

## Getting Started

### Prerequisites

* **Python:** You need Python installed on your system (unless you are on Windows and choose to use the provided CMD file). You can download Python from [python.org](https://www.python.org/downloads/). **The `get_deps` folder contains scripts that can help automate the installation of Python dependencies.**
* **Calibre:** For ePUB processing, you need Calibre installed on your system. The script relies on Calibre's `ebook-convert` tool. You can download it from [calibre-ebook.com](https://calibre-ebook.com/). **The dependency installation scripts in the `get_deps` folder will attempt to install Calibre for you.**
* **PyMuPDF (fitz):** For robust and efficient image extraction from PDFs, it is highly recommended to install PyMuPDF. You can install it using pip: `pip install pymupdf`. While the script has a fallback, installing PyMuPDF will likely provide better results. **The dependency installation scripts in the `get_deps` folder will attempt to install PyMuPDF for you.**
  
### Installation

The `get_deps` folder contains scripts to help you install all the necessary dependencies automatically. Choose the method that suits your operating system:

#### Windows

1.  Navigate to the `get_deps` folder in your terminal or file explorer.
2.  Run the `install_dependencies.cmd` script. This script will first check for Python and optionally try to install it using Winget if not found. Then, it will guide you through running `install_dependencies_p1.py` and `install_dependencies_p2.py` to install the required Python packages and attempt to install Calibre and ImageMagick using Winget.

#### macOS and Linux (and Windows)

1.  Ensure you have Python installed on your system.
2.  Navigate to the `get_deps` folder in your terminal.
3.  Run the `install_dependencies.py` script using the command:
    ```bash
    python install_dependencies.py
    ```
    This script provides an interactive menu to run the following dependency installation scripts:

    * `install_dependencies_p1.py`: Installs core Python dependencies (`PyPDF2`, `ebooklib`, `beautifulsoup4`, `colorama`) and attempts to install Calibre automatically based on your operating system (using Winget on Windows, a direct download script on Linux, and brew cask on macOS). Which is everything require to run the `p1_process_books.py` script.
    * `install_dependencies_p2.py`: Installs additional Python dependencies (`Pillow`, `fitz`, `PyPDF2`, `numpy`, `ebooklib`) and attempts to install **ImageMagick** automatically based on your operating system (using Winget on Windows, `apt-get` on Linux, and Homebrew on macOS). Which is everything required to run the `p2_create_cbz.py` script. 

    Follow the prompts in the `install_dependencies.py` script to install the necessary components. You can run this script again if needed to verify or reinstall specific dependencies.

**Important Notes:**

* The automatic installation of Calibre and ImageMagick might require administrative privileges on some systems.
* If the automatic installation of Calibre fails, please visit [calibre-ebook.com](https://calibre-ebook.com/) for manual installation instructions.
* If the automatic installation of ImageMagick fails, please visit the official ImageMagick website for manual installation instructions.
* The scripts will attempt to install `fitz` (PyMuPDF) automatically, which is highly recommended for better PDF image extraction.

## Usage

The converter offers flexible ways to process your books, leveraging different techniques for optimal results:

### 1. Using the Unified Script (`convert_books.py`)

This is the recommended way for most users to perform a complete conversion:

1.  **Configuration:** Before running, you can customize the conversion process using the interactive `configurator.py` script (see **Configuration**) or by directly editing settings in `p1_process_books.py` and `p2_create_cbz.py`. This includes options for picking the directory for conversion, whether to split the CBZ into multiple files based on chapters, and other settings like the default font size of text for conversion and image quality for CBZs.
2.  **Execution:**
    ```bash
    python convert_books.py
    ```
    **Windows users** can also use the `win_run.cmd` file, which internally executes `convert_books.py`:
    ```cmd
    win_run.cmd
    ```
    This makes it easy to schedule conversions using the Windows Task Scheduler.

### 2. Understanding the Conversion Process (Individual Scripts)

For users who want more control or to understand the underlying mechanics, the conversion is broken down into two main stages:

#### a. Book Processing (`p1_process_books.py`)

This script takes your eBook file (ePUB or PDF) as input and prepares it for CBZ creation.

* **ePUB Handling:** When processing ePUB files, this script utilizes **Calibre** for robust format handling and relies on its `ebook-convert` tool to transform the ePUB into a PDF. It prioritizes metadata from the **OPF** file over the PDF since it often contains more comprehensive information. The script also modifies the font size within the ePUB before conversion.
* **PDF Handling:** For PDF files, the script extracts available metadata if none was created from the OPF file or if one isn't available. It also attempts to extract the **Table of Contents (TOC)** embedded in the PDF to identify chapter boundaries for potential splitting in the next stage.
* **Intermediate Data:** The script processes the book information, including chapter boundaries (if found), and stores it in **two JSON files** (`.chapters.json` and `metadata.json`). These files act as a bridge, holding the necessary data for the CBZ creation script.

#### b. CBZ Creation (`p2_create_cbz.py`)

This script takes the **PDF file** (either converted from ePUB or the original PDF) and the **JSON files** generated by `p1_process_books.py` to create the CBZ file(s).

* **Image Extraction and Optimization:** This script extracts images from the PDF. It prefers to use **PyMuPDF (fitz)** if installed for potentially better results. It then resizes the extracted images to a manageable size and can convert them to JPEG format to optimize the final CBZ file size.
* **Single or Multiple CBZ:** Based on the `split_chapters` setting (which can be configured), this script can create a single CBZ file containing the entire book or split it into multiple CBZ files, with each file representing a chapter using the information from the `.chapters.json` file.

You can run these individual scripts directly if needed, but the `convert_books.py` or `win_run.cmd` script automates this entire flow.

### 3. Configuration (`configurator.py`)

This script provides a user-friendly, interactive way to modify key settings found in `p1_process_books.py` and `p2_create_cbz.py` without needing to directly edit the code. You can set the output directory, choose whether to split chapters, adjust image quality, and other processing parameters.

1.  **Execution:**
    ```bash
    python configurator.py
    ```
    **Windows users** can also just double click `configurator.py`, assuming python is already installed.

2.  Follow the prompts to review and modify the settings.

**Important:** Before running any conversion, ensure you have configured your preferences using `configurator.py` or by manually editing the individual script files. Place the scripts in the same directory as your eBooks or update the settings to point to their location.

## Examples

Let's say you have an ePUB file named `my_book.epub` (and optionally an `my_book.opf` file in the same directory) or a PDF file named `my_book.pdf` in the same directory as the scripts.

1.  **Running individual scripts:**
    * `python p1_process_books.py` (This script will scan the directory for ePUB and PDF files. For each eBook found, it will process it. If an accompanying `.opf` file with the same base name (e.g., `my_book.opf` with `my_book.epub` or `my_book.pdf`) is present, it will be used for enhanced metadata extraction. The script will then convert ePUBs to PDF, if a PDF doesn't already exist, and generate `my_book.metadata.json` and `my_book.chapters.json` for each processed book in the same directory as the input file.)
    * `python p2_create_cbz.py` (This script will scan the directory for PDF files (e.g., `my_book.pdf`) and their corresponding `my_book metadata.json` (and optionally `my_book chapters.json`). For each set of files found, it will create the CBZ file(s) in the directory (e.g., `my_book.cbz` or `my_book_chapter_1.cbz`, `my_book_chapter_2.cbz`, etc.) based on the settings and chapter information. Note that `comicinfo.xml` creation requires `my_book metadata.json`, and chapter splitting requires `my_book chapters.json`.)

2.  **Using the unified script:** After configuring the directory and options (either via `configurator.py` or manual editing), running `python convert_books.py` will process all eligible eBooks in the current directory (or the directory you configured), handling the book processing and CBZ creation steps automatically. The resulting CBZ file(s) (e.g., `my_book.cbz` or `my_book_chapter_1.cbz`, `my_book_chapter_2.cbz`, etc.) will be created in the directory.
   
## Contributing

If you'd like to contribute to this project, please feel free to open issues or submit pull requests.

## License

This project is licensed under the [MIT License](LICENSE).
