# PDFMagus

Desktop PDF manager built with Tkinter/CustomTkinter: view and annotate PDFs
(highlight, underline, strikeout, squiggly), extract text via OCR, and convert,
merge, split, rotate or extract pages from PDFs.

## Requirements

- Python 3.10+
- Windows (the window chrome and Tesseract auto-detection are Windows-specific)
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) installed
  separately if you want to use the OCR button (installing the `pytesseract`
  Python package alone is not enough)

## Setup

```bash
git clone <repo-url>
cd Magus
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Project layout

```
main.py            Entry point
pdfmagus/           Application package
  app.py            Main window, notebook, tab wiring
  theme.py           Colors, fonts, icons
  tabs/              Edit / Convert / Logs tabs
  operations/         PDF logic (merge, split, rotate, extract, format conversion)
  ocr/                Tesseract detection and OCR execution
  reading/            Reading-history persistence (reader_history.json)
```

## Building the executable

Requires `pyinstaller` (`pip install pyinstaller`):

```bash
pyinstaller PDFMagus.spec --noconfirm
```

The built executable is written to `dist/PDFMagus.exe`.
