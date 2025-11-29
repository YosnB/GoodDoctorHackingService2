# GoodDoctorHackingService

An OCR and image analysis tool with encode/decode functionality.

## Features

- **Text Recognition (OCR)** — Extract text from images using Tesseract (pytesseract)
- **Image Analysis** — Analyze image properties and metadata  
- **Encode/Decode** — Convert text between multiple formats (Base64, Hex, Binary, ROT13, ROT18, ROT47, Caesar, URL, Morse, Alphabet↔Number)

## Requirements

- Python 3.12+
- PyQt5
- OpenCV
- Tesseract OCR (Tesseract engine + `pytesseract`)
- NumPy
- Pillow
- pillow-heif

## Installation

### From PyPI (when published)

```bash
pip install gooddoctor-hacking-service
```

### Local Development

```bash
git clone https://github.com/YosnB/GoodDoctorHackingService2.git
cd GoodDoctorHackingService2
pip install -e .
```

### Using requirements.txt

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Tesseract setup

This project now uses the Tesseract OCR engine via the `pytesseract` Python wrapper instead of EasyOCR.

- Install the Tesseract engine on your system:
	- Windows: download installer from https://github.com/tesseract-ocr/tesseract/releases or use `choco install tesseract`.
	- macOS: `brew install tesseract`
	- Linux (Debian/Ubuntu): `sudo apt-get install tesseract-ocr tesseract-ocr-jpn`

- Ensure the appropriate language data is installed (e.g. `jpn` for Japanese). If Japanese data is not installed, the app will fall back to English.

- Install Python dependencies in the project environment:

```powershell
pip install -r requirements.txt
```

## Project Structure

```
.
├── main.py                  # Main application entry point
├── windows/
│   ├── __init__.py
│   ├── decode_window.py     # Decode/Encode window
│   ├── image_window.py      # Image analysis window
│   ├── moji_window.py       # OCR window
│   └── algorithms/          # Encoding/Decoding algorithms
│       ├── base64_en.py
│       ├── base64_de.py
│       ├── binary_en.py
│       ├── binary_de.py
│       ├── hex_en.py
│       ├── hex_de.py
│       ├── morse_en.py
│       ├── morse_de.py
│       ├── url_en.py
│       ├── url_de.py
│       ├── Z1_ROT13.py
│       ├── Z1_ROT18.py
│       ├── Z1_ROT47.py
│       ├── Z2_caesar_en.py
│       └── alpha_num_en.py / alpha_num_de.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests (if available):

```bash
pytest
```

Format code:

```bash
black .
```

Type check:

```bash
mypy windows/
```

## License

MIT License — See LICENSE file for details.

## Author

YosnB
