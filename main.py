from pathlib import Path

from pdfmagus.app import PDFMagus

BASE_DIR = Path(__file__).resolve().parent


def main():
    app = PDFMagus(base_dir=BASE_DIR)
    app.mainloop()


if __name__ == "__main__":
    main()
