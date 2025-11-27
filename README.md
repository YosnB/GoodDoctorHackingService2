# GoodDoctorHackingService

An OCR and image analysis tool with encode/decode functionality.

## Features

- **Text Recognition (OCR)** — Extract text from images using EasyOCR
- **Image Analysis** — Analyze image properties and metadata  
- **Encode/Decode** — Convert text between multiple formats (Base64, Hex, Binary, ROT13, ROT18, ROT47, Caesar, URL, Morse, Alphabet↔Number)

## Requirements

- Python 3.12+
- PyQt5
- OpenCV
- EasyOCR
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
