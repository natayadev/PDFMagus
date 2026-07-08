import tkinter as tk
from tkinter import filedialog

from pdfmagus.theme import COLORS
from pdfmagus.widgets.buttons import secondary_button


class OutputFolderPicker:
    """Shared 'Output folder: [path] [Browse]' row used by every convert panel."""

    def __init__(self, parent, label_text="Output folder:", on_change=None):
        self.folder = None
        self.on_change = on_change

        tk.Label(parent, text=label_text, bg=COLORS["white"], fg=COLORS["black"]).pack(anchor="w")

        row = tk.Frame(parent, bg=COLORS["white"])
        row.pack(fill="x", pady=(0, 10))

        self.label = tk.Label(
            row, text="Not selected", bg=COLORS["white"], fg=COLORS["text_muted"], font=("Arial", 10)
        )
        self.label.pack(side="left", fill="x", expand=True)

        secondary_button(row, "Browse", self._browse, width=80, height=35).pack(side="right", padx=5)

    def _browse(self):
        folder = filedialog.askdirectory(title="Output folder")
        if folder:
            self.folder = folder
            self.label.configure(text=folder)
            if self.on_change:
                self.on_change(folder)
