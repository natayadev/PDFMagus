import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk

from pdfmagus.operations.merge import merge_pdfs
from pdfmagus.operations.page_range import get_pdf_pages
from pdfmagus.tabs.convert_panels.preview import render_pdf_thumbnails
from pdfmagus.theme import COLORS
from pdfmagus.widgets.buttons import primary_button, run_button, secondary_button
from pdfmagus.widgets.output_folder_picker import OutputFolderPicker


class MergePanel:
    def __init__(self, preview_canvas, log_event):
        self.preview_canvas = preview_canvas
        self.log_event = log_event

        self.file_list = []

    def build(self, parent):
        btn_frame = tk.Frame(parent, bg=COLORS["white"])
        btn_frame.pack(fill="x", pady=(0, 10))

        primary_button(btn_frame, "Add PDFs", self.add_pdfs, width=120).pack(side="left", padx=5)
        secondary_button(btn_frame, "↑", self.move_up, width=50, font=ctk.CTkFont(family="Arial", size=14)).pack(
            side="left", padx=2
        )
        secondary_button(btn_frame, "↓", self.move_down, width=50, font=ctk.CTkFont(family="Arial", size=14)).pack(
            side="left", padx=2
        )
        secondary_button(
            btn_frame, "Remove", self.remove_selected, width=90, hover_color=COLORS["danger_hover_light"]
        ).pack(side="left", padx=5)

        tree_frame = tk.Frame(parent, bg=COLORS["white"])
        tree_frame.pack(fill="both", expand=True, pady=(0, 10))

        scroll = tk.Scrollbar(tree_frame)
        scroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(tree_frame, columns=("pages", "size"), height=10, yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.configure(command=self.tree.yview)

        self.tree.heading("#0", text="File")
        self.tree.heading("pages", text="Pages")
        self.tree.heading("size", text="Size")
        self.tree.column("#0", width=200)
        self.tree.column("pages", width=80)
        self.tree.column("size", width=80)

        options_frame = tk.Frame(parent, bg=COLORS["white"])
        options_frame.pack(fill="x", pady=10)

        tk.Label(options_frame, text="Output prefix:", bg=COLORS["white"], fg=COLORS["black"]).pack(anchor="w")
        self.entry_prefix = ctk.CTkEntry(options_frame, height=35, font=ctk.CTkFont(family="Arial", size=11))
        self.entry_prefix.pack(fill="x", pady=(0, 10))
        self.entry_prefix.insert(0, "[BASENAME]_merge")

        self.output_folder_picker = OutputFolderPicker(options_frame)

        run_button(parent, "Run", self.execute_merge).pack(pady=10)

    def add_pdfs(self):
        files = filedialog.askopenfilenames(title="Select PDFs", filetypes=[("PDF", "*.pdf")])
        for file in files:
            self.tree.insert(
                "",
                "end",
                text=os.path.basename(file),
                values=(get_pdf_pages(file), f"{os.path.getsize(file) / 1024 / 1024:.1f}MB"),
            )
            self.file_list.append(file)
        self.log_event(f"Added {len(files)} PDF(s) to merge")
        self.refresh_preview()

    def remove_selected(self):
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            self.tree.delete(selected[0])
            self.file_list.pop(index)
            self.log_event("PDF removed from merge")

    def move_up(self):
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            if index > 0:
                self.file_list[index], self.file_list[index - 1] = self.file_list[index - 1], self.file_list[index]
                self._refresh_tree()

    def move_down(self):
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            if index < len(self.file_list) - 1:
                self.file_list[index], self.file_list[index + 1] = self.file_list[index + 1], self.file_list[index]
                self._refresh_tree()

    def _refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for file in self.file_list:
            self.tree.insert(
                "",
                "end",
                text=os.path.basename(file),
                values=(get_pdf_pages(file), f"{os.path.getsize(file) / 1024 / 1024:.1f}MB"),
            )

    def execute_merge(self):
        if not self.file_list:
            messagebox.showwarning("Warning", "Add at least one PDF")
            return
        if not self.output_folder_picker.folder:
            messagebox.showwarning("Warning", "Select an output folder")
            return

        try:
            prefix = self.entry_prefix.get()
            output_file = os.path.join(self.output_folder_picker.folder, f"{prefix}.pdf")
            merge_pdfs(self.file_list, output_file)

            self.log_event(f"PDF merged: {os.path.basename(output_file)}")
            messagebox.showinfo("Success", f"PDFs merged into:\n{output_file}")
        except Exception as e:
            self.log_event(f"Error merging: {e}")
            messagebox.showerror("Error", str(e))

    def refresh_preview(self):
        entries = [(f, 0, None) for f in self.file_list[:5]]
        render_pdf_thumbnails(self.preview_canvas, entries)
