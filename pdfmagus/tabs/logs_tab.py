import tkinter as tk
from tkinter import scrolledtext

import customtkinter as ctk

from pdfmagus.theme import COLORS


class LogsTab(tk.Frame):
    def __init__(self, notebook, on_clear):
        super().__init__(notebook, bg=COLORS["white"])
        notebook.add(self, text="Logs")

        top_frame = tk.Frame(self, bg=COLORS["white"])
        top_frame.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkButton(
            top_frame,
            text="Clear logs",
            width=120,
            height=32,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=ctk.CTkFont(family="Arial", size=12),
            command=on_clear,
        ).pack(side="right")

        self.text_area = scrolledtext.ScrolledText(
            self,
            wrap=tk.WORD,
            state="disabled",
            bg=COLORS["white"],
            fg=COLORS["black"],
            font=("Consolas", 10),
        )
        self.text_area.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def append_line(self, line):
        self.text_area.configure(state="normal")
        self.text_area.insert(tk.END, line)
        self.text_area.see(tk.END)
        self.text_area.configure(state="disabled")

    def clear(self):
        self.text_area.configure(state="normal")
        self.text_area.delete("1.0", tk.END)
        self.text_area.configure(state="disabled")
