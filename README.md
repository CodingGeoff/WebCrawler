# Web 2 Markdown Pro 🚀

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](https://choosealicense.com/licenses/mit/)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-brightgreen.svg)](https://www.python.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/CodingGeoff/WebCrawler/pulls)

**The ultimate tool for converting any webpage into clean, portable, and beautifully formatted Markdown.**

Tired of cluttered web articles, ads, and pop-ups? Web 2 Markdown Pro intelligently extracts the core content from any URL and converts it into a pristine Markdown file, ready for your note-taking app, static site generator, or personal archive.

## ✨ Key Features

- **One-Click Conversion**: Simply paste a URL and get clean Markdown in seconds.
- **Robust Content Extraction**: Powered by `trafilatura`, it intelligently finds the main article content, filtering out ads, navbars, and other noise.
- **Advanced Fetching System**: If one method fails, it automatically tries two fallback methods (`requests` and a full browser simulation via `DrissionPage`) to handle even the most stubborn JavaScript-heavy sites.
- **Powerful Image Handling**:
  - **Download Images**: Automatically download all images to a local folder and update the links.
  - **Keep Original Links**: Retain the original image URLs.
  - **Strip Images**: Remove all images for a text-only experience.
- **Batch Processing**: Convert a whole list of URLs from a `.txt` file in one go, perfect for large archiving tasks.
- **Automatic Table of Contents (TOC)**: Generates a clickable TOC for articles with headings, making navigation a breeze.
- **YAML Frontmatter**: Includes a clean `---` header with title, source URL, and conversion date, perfect for Obsidian, Jekyll, Hugo, and other platforms.
- **Link Cleaner**: Automatically removes tracking parameters (like `utm_source`) from hyperlinks.
- **Modern UI**: A clean, intuitive interface built with CustomTkinter, featuring:
  - Light & Dark Modes
  - Conversion History Dropdown
  - Progress Bar and Status Updates
  - Word & Character Count

## 🏁 Getting Started

### For Users (Recommended)

1. Navigate to the [**Latest Release**](https://github.com/CodingGeoff/WebCrawler/releases/latest).
2. Download the `Web-2-Markdown-Pro.exe` file from the **Assets** section.
3. No installation needed! Just double-click the `.exe` to run the application.

### For Developers (Running from Source)

If you want to run the application from the source code and customize it:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/CodingGeoff/WebCrawler.git
   cd WebCrawler
   ```
2. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```
3. **Install the required dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   *(You will need to create a `requirements.txt` file with the content below).*
4. **Run the application:**

   ```bash
   python app.py
   ```

## 💻 How to Use

1. **Paste URL**: Paste a web page link into the input field.
2. **Select Options**:
   - Choose your desired image handling method.
   - Check/uncheck TOC generation or link cleaning.
3. **Convert**: Click the "Start Conversion" button.
4. **Save or Copy**: Once complete, the Markdown will appear. You can use the buttons at the bottom to save it as a `.md` file or copy the entire content to your clipboard.

## 🛠️ Building From Source

To build your own `.exe` file, ensure you have PyInstaller and the necessary project structure:

```
/WebCrawler/
|-- app.py
|-- webcrawler.ico
|-- /drivers/
|   |-- (chromedriver.exe, etc.)
```

Then, run the following command in your terminal:

```bash
pyinstaller --noconfirm --onefile --windowed --name "Web2Markdown-Pro" --icon="webcrawler.ico" --add-data "drivers;drivers" app.py
```

The final executable will be located in the `dist` folder.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/CodingGeoff/WebCrawler/issues).

## 📄 License

Distributed under the MIT License.
