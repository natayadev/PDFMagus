from tkfontawesome import icon_to_image


COLORS = {
    "primary": "#E34A6F",
    "primary_hover": "#C93A5F",
    "hover": "#f0f9f4",
    "white": "white",
    "black": "black",
    "gray_light": "#f0f0f0",
    "gray_medium": "#444444",
    "gray_dark": "#808080",
    "background": "#E34A6F",
    "canvas": "#e0e0e0",
    "disabled": "#F7B2BD",
    "danger": "#dc2626",
    "danger_bright": "#EF4444",
    "danger_hover": "#8B0000",
    "danger_hover_light": "#fef2f2",
    "border": "#666666",
    "text_muted": "gray",
    "selection": "red",
}

FONTS = {
    "tab_label": ("Arial", 12, "bold"),
    "button_active": ("Arial", 12, "bold"),
    "button_inactive": ("Arial", 11, "bold"),
    "label": ("Arial", 12, "bold"),
    "small": ("Arial", 10, "normal"),
}


def load_icons():
    return {
        "open_pdf": icon_to_image("file-alt", fill=COLORS["primary"], scale_to_width=20),
        "save_pdf": icon_to_image("save", fill=COLORS["primary"], scale_to_width=20),
        "prev_page": icon_to_image("chevron-left", fill=COLORS["primary"], scale_to_width=20),
        "next_page": icon_to_image("chevron-right", fill=COLORS["primary"], scale_to_width=20),
        "zoom_in": icon_to_image("plus", fill=COLORS["primary"], scale_to_width=20),
        "zoom_out": icon_to_image("minus", fill=COLORS["primary"], scale_to_width=20),
        "merge": icon_to_image("layer-group", fill=COLORS["primary"], scale_to_width=20),
        "split": icon_to_image("cut", fill=COLORS["primary"], scale_to_width=20),
        "highlight": icon_to_image("highlighter", fill=COLORS["primary"], scale_to_width=20),
        "export": icon_to_image("file-download", fill=COLORS["primary"], scale_to_width=20),
        "trash": icon_to_image("trash-alt", fill=COLORS["danger_bright"], scale_to_width=20),
        "clear": icon_to_image("eraser", fill=COLORS["danger"], scale_to_width=20),
        "add": icon_to_image("plus", fill=COLORS["primary"], scale_to_width=20),
        "remove": icon_to_image("minus", fill=COLORS["danger"], scale_to_width=20),
        "undo": icon_to_image("undo", fill=COLORS["primary"], scale_to_width=20),
        "save_pdf_disabled": icon_to_image("save", fill=COLORS["disabled"], scale_to_width=20),
        "export_disabled": icon_to_image("file-download", fill=COLORS["disabled"], scale_to_width=20),
        "clear_disabled": icon_to_image("eraser", fill=COLORS["disabled"], scale_to_width=20),
        "undo_disabled": icon_to_image("undo", fill=COLORS["disabled"], scale_to_width=20),
        "prev_page_disabled": icon_to_image("chevron-left", fill=COLORS["disabled"], scale_to_width=20),
        "next_page_disabled": icon_to_image("chevron-right", fill=COLORS["disabled"], scale_to_width=20),
        "minimize": icon_to_image("window-minimize", fill="white", scale_to_width=15),
        "maximize": icon_to_image("window-maximize", fill="white", scale_to_width=15),
        "close": icon_to_image("times", fill="white", scale_to_width=15),
        "highlight_mode": icon_to_image("highlighter", fill=COLORS["primary"], scale_to_width=20),
        "underline_mode": icon_to_image("pen", fill=COLORS["primary"], scale_to_width=20),
        "strikeout_mode": icon_to_image("ban", fill=COLORS["primary"], scale_to_width=20),
        "rotate": icon_to_image("sync-alt", fill=COLORS["primary"], scale_to_width=20),
        "extract": icon_to_image("file-export", fill=COLORS["primary"], scale_to_width=20),
        "word": icon_to_image("file-word", fill=COLORS["primary"], scale_to_width=20),
        "epub": icon_to_image("book", fill=COLORS["primary"], scale_to_width=20),
        "image": icon_to_image("file-image", fill=COLORS["primary"], scale_to_width=20),
        "ocr": icon_to_image("font", fill=COLORS["primary"], scale_to_width=22),
    }
