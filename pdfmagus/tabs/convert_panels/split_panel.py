import os
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

from pdfmagus.operations.page_range import get_pdf_pages
from pdfmagus.operations.split import split_pdf
from pdfmagus.tabs.convert_panels.preview import render_pdf_thumbnails
from pdfmagus.theme import COLORS
from pdfmagus.widgets.buttons import primary_button, run_button
from pdfmagus.widgets.output_folder_picker import OutputFolderPicker


class SplitPanel:
    def __init__(self, preview_canvas, log_event):
        self.preview_canvas = preview_canvas
        self.log_event = log_event

        self.pdf_file = None

    def build(self, parent):
        file_frame = tk.Frame(parent, bg=COLORS["white"])
        file_frame.pack(fill="x", pady=(0, 10))

        primary_button(file_frame, "Browse PDF", self.select_pdf, width=100).pack(side="left", padx=5)

        self.lbl_file = tk.Label(
            file_frame, text="Not selected", bg=COLORS["white"], fg=COLORS["text_muted"], font=("Arial", 10)
        )
        self.lbl_file.pack(side="left", fill="x", expand=True, padx=10)

        mode_frame = tk.Frame(parent, bg=COLORS["white"])
        mode_frame.pack(fill="x", pady=10)

        tk.Label(
            mode_frame, text="Split mode:", bg=COLORS["white"], fg=COLORS["black"], font=("Arial", 11, "bold")
        ).pack(anchor="w")

        self.mode_var = tk.StringVar(value="range")

        tk.Radiobutton(
            mode_frame, text="By range (1,3-5,*)", variable=self.mode_var, value="range",
            bg=COLORS["white"], command=self.on_mode_change,
        ).pack(anchor="w")
        tk.Radiobutton(
            mode_frame, text="Even pages", variable=self.mode_var, value="even",
            bg=COLORS["white"], command=self.on_mode_change,
        ).pack(anchor="w")
        tk.Radiobutton(
            mode_frame, text="Odd pages", variable=self.mode_var, value="odd",
            bg=COLORS["white"], command=self.on_mode_change,
        ).pack(anchor="w")
        tk.Radiobutton(
            mode_frame, text="By size (MB)", variable=self.mode_var, value="size",
            bg=COLORS["white"], command=self.on_mode_change,
        ).pack(anchor="w")

        input_frame = tk.Frame(parent, bg=COLORS["white"])
        input_frame.pack(fill="x", pady=10)

        self.lbl_input = tk.Label(input_frame, text="Page range:", bg=COLORS["white"], fg=COLORS["black"])
        self.lbl_input.pack(anchor="w")

        self.entry_input = ctk.CTkEntry(input_frame, height=35, font=ctk.CTkFont(family="Arial", size=11))
        self.entry_input.pack(fill="x", pady=(0, 10))
        self.entry_input.insert(0, "1-*")

        folder_frame = tk.Frame(parent, bg=COLORS["white"])
        folder_frame.pack(fill="x", pady=10)

        self.output_folder_picker = OutputFolderPicker(folder_frame)

        run_button(parent, "Run", self.execute_split).pack(pady=10)

    def on_mode_change(self):
        mode = self.mode_var.get()
        if mode == "range":
            self.lbl_input.configure(text="Page range (e.g. 1,3-5,*):")
            self.entry_input.delete(0, "end")
            self.entry_input.insert(0, "1-*")
        elif mode in ("even", "odd"):
            self.lbl_input.configure(text="")
            self.entry_input.configure(state="disabled")
        elif mode == "size":
            self.lbl_input.configure(text="Size (MB):")
            self.entry_input.configure(state="normal")
            self.entry_input.delete(0, "end")
            self.entry_input.insert(0, "5")

    def select_pdf(self):
        file = filedialog.askopenfilename(title="Select PDF", filetypes=[("PDF", "*.pdf")])
        if file:
            self.pdf_file = file
            pages = get_pdf_pages(file)
            self.lbl_file.configure(text=f"{os.path.basename(file)} ({pages} pages)")
            self.entry_input.delete(0, "end")
            self.entry_input.insert(0, f"1-{pages}")
            self.refresh_preview()

    def execute_split(self):
        if not self.pdf_file:
            messagebox.showwarning("Warning", "Select a PDF")
            return
        if not self.output_folder_picker.folder:
            messagebox.showwarning("Warning", "Select an output folder")
            return

        try:
            mode = self.mode_var.get()
            output_folder = self.output_folder_picker.folder
            split_pdf(self.pdf_file, mode, self.entry_input.get(), output_folder)

            basename = os.path.splitext(os.path.basename(self.pdf_file))[0]
            self.log_event(f"PDF split: {basename}")
            messagebox.showinfo("Success", f"PDF split into {output_folder}")
        except Exception as e:
            self.log_event(f"Error splitting: {e}")
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
