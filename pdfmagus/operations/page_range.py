import fitz


def get_pdf_pages(file_path):
    try:
        doc = fitz.open(file_path)
        pages = len(doc)
        doc.close()
        return pages
    except Exception:
        return 0


def parse_page_range(range_str, total_pages):
    pages = []
    range_str = range_str.strip()

    for part in range_str.split(","):
        part = part.strip()
        if part == "*":
            pages.extend(range(1, total_pages + 1))
        elif "-" in part:
            start, end = part.split("-")
            start = int(start.strip())
            end = int(end.strip()) if end.strip() != "*" else total_pages
            pages.extend(range(start, min(end + 1, total_pages + 1)))
        else:
            page = int(part)
            if page <= total_pages:
                pages.append(page)

    return sorted(set(pages))
