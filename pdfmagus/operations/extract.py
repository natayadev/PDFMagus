import os

import fitz

from pdfmagus.operations.page_range import parse_page_range


def extract_pages(path, pages_input, output_folder):
    doc = fitz.open(path)
    total_pages = len(doc)
    pages = parse_page_range(pages_input, total_pages)

    new_doc = fitz.open()
    for page_num in pages:
        new_doc.insert_pdf(doc, from_page=page_num - 1, to_page=page_num - 1)

    basename = os.path.splitext(os.path.basename(path))[0]
    output_path = os.path.join(output_folder, f"{basename}_extracted.pdf")
    new_doc.save(output_path)
    new_doc.close()
    doc.close()

    return output_path
