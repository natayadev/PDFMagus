import os
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

from pdfmagus.operations.extract import extract_pages
from pdfmagus.operations.page_range import get_pdf_pages
from pdfmagus.tabs.convert_panels.preview import render_pdf_thumbnails
from pdfmagus.theme import COLORS


class ExtractPanel:
    def __init__(self, preview_canvas, log_event):
        self.preview_canvas = preview_canvas
        self.log_event = log_event

        self.pdf_file = None
        self.output_folder = None

    def build(self, parent):
        file_frame = tk.Frame(parent, bg=COLORS["white"])
        file_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(
            file_frame,
            text="Browse PDF",
            width=100,
            height=40,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=ctk.CTkFont(family="Arial", size=11),
            command=self.select_pdf,
        ).pack(side="left", padx=5)

        self.lbl_file = tk.Label(
            file_frame, text="Not selected", bg=COLORS["white"], fg=COLORS["text_muted"], font=("Arial", 10)
        )
        self.lbl_file.pack(side="left", fill="x", expand=True, padx=10)

        pages_frame = tk.Frame(parent, bg=COLORS["white"])
        pages_frame.pack(fill="x", pady=10)

        tk.Label(pages_frame, text="Pages (e.g. 1-3,5,7-*):", bg=COLORS["white"], fg=COLORS["black"]).pack(anchor="w")
        self.entry_pages = ctk.CTkEntry(pages_frame, height=35, font=ctk.CTkFont(family="Arial", size=11))
        self.entry_pages.pack(fill="x", pady=(0, 10))
        self.entry_pages.insert(0, "1-*")

        folder_frame = tk.Frame(parent, bg=COLORS["white"])
        folder_frame.pack(fill="x", pady=10)

        tk.Label(folder_frame, text="Output folder:", bg=COLORS["white"], fg=COLORS["black"]).pack(anchor="w")

        folder_selector = tk.Frame(folder_frame, bg=COLORS["white"])
        folder_selector.pack(fill="x", pady=(0, 10))

        self.lbl_folder = tk.Label(
            folder_selector, text="Not selected", bg=COLORS["white"], fg=COLORS["text_muted"], font=("Arial", 10)
        )
        self.lbl_folder.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            folder_selector,
            text="Browse",
            width=80,
            height=35,
            fg_color=COLORS["white"],
            hover_color=COLORS["hover"],
            font=ctk.CTkFont(family="Arial", size=10),
            command=self.select_output_folder,
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            parent,
            text="Run",
            width=200,
            height=45,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
            command=self.execute_extract,
        ).pack(pady=10)

    def select_pdf(self):
        file = filedialog.askopenfilename(title="Select PDF", filetypes=[("PDF", "*.pdf")])
        if file:
            self.pdf_file = file
            pages = get_pdf_pages(file)
            self.lbl_file.configure(text=f"{os.path.basename(file)} ({pages} pages)")
            self.entry_pages.delete(0, "end")
            self.entry_pages.insert(0, f"1-{pages}")
            self.refresh_preview()

    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Output folder")
        if folder:
            self.output_folder = folder
            self.lbl_folder.configure(text=folder)

    def execute_extract(self):
        if not self.pdf_file:
            messagebox.showwarning("Warning", "Select a PDF")
            return
        if not self.output_folder:
            messagebox.showwarning("Warning", "Select an output folder")
            return

        try:
            output_path = extract_pages(self.pdf_file, self.entry_pages.get(), self.output_folder)

            basename = os.path.splitext(os.path.basename(self.pdf_file))[0]
            self.log_event(f"Pages extracted: {basename}")
            messagebox.showinfo("Success", f"Pages extracted to:\n{output_path}")
        except Exception as e:
            self.log_event(f"Error extracting: {e}")
            messagebox.showerror("Error", str(e))

    def refresh_preview(self):
        if not self.pdf_file:
            return
        try:
            pages = get_pdf_pages(self.pdf_file)
            count = min(3, pages)
            entries = [(self.pdf_file, i, f"Page {i + 1}") for i in range(count)]
            extra_text = f"... +{pages - 3} more" if pages > 3 else None
            render_pdf_thumbnails(self.preview_canvas, entries, extra_text)
        except Exception:
            pass
