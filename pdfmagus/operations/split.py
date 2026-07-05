import os

import fitz

from pdfmagus.operations.page_range import parse_page_range


def split_pdf(path, mode, pages_input, output_folder):
    doc = fitz.open(path)
    total_pages = len(doc)
    basename = os.path.splitext(os.path.basename(path))[0]

    if mode == "range":
        pages = parse_page_range(pages_input, total_pages)
        for index, page_num in enumerate(pages, 1):
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=page_num - 1, to_page=page_num - 1)
            out = os.path.join(output_folder, f"{basename}_split_{index:03d}.pdf")
            new_doc.save(out)
            new_doc.close()
    elif mode == "even":
        for i in range(1, total_pages, 2):
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=i, to_page=i)
            out = os.path.join(output_folder, f"{basename}_even_{i + 1:03d}.pdf")
            new_doc.save(out)
            new_doc.close()
    elif mode == "odd":
        for i in range(0, total_pages, 2):
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=i, to_page=i)
            out = os.path.join(output_folder, f"{basename}_odd_{i + 1:03d}.pdf")
            new_doc.save(out)
            new_doc.close()

    doc.close()
