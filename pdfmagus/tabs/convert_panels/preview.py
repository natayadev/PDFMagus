import io

import fitz
from PIL import Image, ImageTk

THUMBNAIL_WIDTH = 130
THUMBNAIL_MATRIX_SCALE = 0.15


def _render_thumbnail(file_path, page_index):
    doc = fitz.open(file_path)
    page = doc[page_index]
    mat = fitz.Matrix(THUMBNAIL_MATRIX_SCALE, THUMBNAIL_MATRIX_SCALE)
    pix = page.get_pixmap(matrix=mat)
    img = Image.open(io.BytesIO(pix.tobytes("ppm")))
    img = img.resize((THUMBNAIL_WIDTH, int(THUMBNAIL_WIDTH * img.height / img.width)), Image.Resampling.LANCZOS)
    doc.close()
    return img


def render_pdf_thumbnails(canvas, entries, extra_text=None):
    canvas.delete("all")
    canvas.image_list = []

    y = 5
    for file_path, page_index, label in entries:
        try:
            img = _render_thumbnail(file_path, page_index)

            if label:
                canvas.create_text(70, y - 10, text=label, font=("Arial", 8), fill="gray")

            photo = ImageTk.PhotoImage(img)
            canvas.create_image(10, y, anchor="nw", image=photo)
            canvas.image_list.append(photo)

            y += img.height + 5
        except Exception:
            pass

    if extra_text:
        canvas.create_text(70, y, text=extra_text, font=("Arial", 7), fill="gray")

    canvas.configure(scrollregion=canvas.bbox("all"))


def render_original_page_preview(canvas, file_path):
    canvas.delete("all")
    canvas.image_list = []

    try:
        img = _render_thumbnail(file_path, 0)
        photo = ImageTk.PhotoImage(img)

        canvas.create_text(70, 5, text="Original", font=("Arial", 9, "bold"), fill="gray")
        canvas.create_image(10, 25, anchor="nw", image=photo)
        canvas.image_list = [photo]

        canvas.configure(scrollregion=canvas.bbox("all"))
    except Exception:
        pass
