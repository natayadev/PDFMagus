import gc

import fitz


def merge_pdfs(files, output_path):
    result = fitz.open()
    for file in files:
        doc = fitz.open(file)
        result.insert_pdf(doc)
        doc.close()

    result.save(output_path)
    result.close()
    gc.collect()
