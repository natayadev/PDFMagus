import os

import fitz

from pdfmagus.operations.page_range import parse_page_range


def rotate_pdf(path, pages_input, degrees, output_folder):
    doc = fitz.open(path)
    pages = parse_page_range(pages_input, len(doc))

    for page_num in pages:
        page = doc[page_num - 1]
        page.set_rotation(degrees)

    basename = os.path.splitext(os.path.basename(path))[0]
    output_path = os.path.join(output_folder, f"{basename}_rotated.pdf")
    doc.save(output_path)
    doc.close()

    return output_path
