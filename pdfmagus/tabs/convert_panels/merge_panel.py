import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk

from pdfmagus.operations.merge import merge_pdfs
from pdfmagus.operations.page_range import get_pdf_pages
from pdfmagus.tabs.convert_panels.preview import render_pdf_thumbnails
from pdfmagus.theme import COLORS


class MergePanel:
    def __init__(self, preview_canvas, log_event):
        self.preview_canvas = preview_canvas
        self.log_event = log_event

        self.file_list = []
        self.output_folder = None

    def build(self, parent):
        btn_frame = tk.Frame(parent, bg=COLORS["white"])
        btn_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(
            btn_frame,
            text="Add PDFs",
            width=120,
            height=40,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=ctk.CTkFont(family="Arial", size=11),
            command=self.add_pdfs,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="↑",
            width=50,
            height=40,
            fg_color=COLORS["white"],
            hover_color=COLORS["hover"],
            font=ctk.CTkFont(family="Arial", size=14),
            command=self.move_up,
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            btn_frame,
            text="↓",
            width=50,
            height=40,
            fg_color=COLORS["white"],
            hover_color=COLORS["hover"],
            font=ctk.CTkFont(family="Arial", size=14),
            command=self.move_down,
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            btn_frame,
            text="Remove",
            width=90,
            height=40,
            fg_color=COLORS["white"],
            hover_color=COLORS["danger_hover_light"],
            font=ctk.CTkFont(family="Arial", size=11),
            command=self.remove_selected,
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

        tk.Label(options_frame, text="Output folder:", bg=COLORS["white"], fg=COLORS["black"]).pack(anchor="w")

        folder_frame = tk.Frame(options_frame, bg=COLORS["white"])
        folder_frame.pack(fill="x", pady=(0, 10))

        self.lbl_folder = tk.Label(
            folder_frame, text="Not selected", bg=COLORS["white"], fg=COLORS["text_muted"], font=("Arial", 10)
        )
        self.lbl_folder.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            folder_frame,
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
            command=self.execute_merge,
        ).pack(pady=10)

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

    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Output folder")
        if folder:
            self.output_folder = folder
            self.lbl_folder.configure(text=folder)

    def execute_merge(self):
        if not self.file_list:
            messagebox.showwarning("Warning", "Add at least one PDF")
            return
        if not self.output_folder:
            messagebox.showwarning("Warning", "Select an output folder")
            return

        try:
            prefix = self.entry_prefix.get()
            output_file = os.path.join(self.output_folder, f"{prefix}.pdf")
            merge_pdfs(self.file_list, output_file)

            self.log_event(f"PDF merged: {os.path.basename(output_file)}")
            messagebox.showinfo("Success", f"PDFs merged into:\n{output_file}")
        except Exception as e:
            self.log_event(f"Error merging: {e}")
            messagebox.showerror("Error", str(e))

    def refresh_preview(self):
        entries = [(f, 0, None) for f in self.file_list[:5]]
        render_pdf_thumbnails(self.preview_canvas, entries)
