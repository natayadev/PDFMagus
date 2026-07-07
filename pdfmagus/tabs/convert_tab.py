import tkinter as tk

import customtkinter as ctk

from pdfmagus.tabs.convert_panels.extract_panel import ExtractPanel
from pdfmagus.tabs.convert_panels.format_panel import FormatConversionPanel
from pdfmagus.tabs.convert_panels.merge_panel import MergePanel
from pdfmagus.tabs.convert_panels.rotate_panel import RotatePanel
from pdfmagus.tabs.convert_panels.split_panel import SplitPanel
from pdfmagus.theme import COLORS, FONTS
from pdfmagus.widgets.tooltip import attach_tooltip

OPERATIONS = [
    ("formats", "word", "Convert to PDF"),
    ("merge", "merge", "Merge PDFs"),
    ("split", "split", "Split PDF"),
    ("rotate", "rotate", "Rotate pages"),
    ("extract", "extract", "Extract pages"),
]


class ConvertTab(tk.Frame):
    def __init__(self, notebook, icons, log_event):
        super().__init__(notebook, bg=COLORS["white"])
        notebook.add(self, text="Convert")

        self.icons = icons
        self.log_event = log_event

        middle_section = tk.Frame(self, bg=COLORS["white"])
        middle_section.pack(fill="both", expand=True, padx=10, pady=5)

        self._build_sidebar(middle_section)

        main_container = tk.Frame(middle_section, bg=COLORS["white"])
        main_container.pack(side="right", fill="both", expand=True, padx=10, pady=5)

        self.left_panel = tk.Frame(main_container, bg=COLORS["white"])
        self.left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right_panel = tk.Frame(main_container, bg=COLORS["white"], width=480)
        right_panel.pack(side="right", fill="both", padx=(10, 0))
        right_panel.pack_propagate(False)

        ctk.CTkLabel(right_panel, text="Preview", font=FONTS["label"], text_color=COLORS["black"]).pack(pady=5)

        self.preview_canvas = tk.Canvas(right_panel, bg=COLORS["canvas"], highlightthickness=0)
        self.preview_canvas.pack(fill="both", expand=True)

        self.panels = {
            "formats": FormatConversionPanel(self.icons, self.preview_canvas, self.log_event),
            "merge": MergePanel(self.preview_canvas, self.log_event),
            "split": SplitPanel(self.preview_canvas, self.log_event),
            "rotate": RotatePanel(self.preview_canvas, self.log_event),
            "extract": ExtractPanel(self.preview_canvas, self.log_event),
        }

        self.current_operation = "formats"
        self.show_operation("formats")

    def _build_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=COLORS["white"])
        sidebar.pack(side="left", fill="y", padx=10, pady=10)

        self.operation_buttons = {}
        for op_id, icon_name, tooltip in OPERATIONS:
            btn = ctk.CTkButton(
                sidebar,
                text="",
                image=self.icons[icon_name],
                width=40,
                height=40,
                fg_color=COLORS["white"],
                hover_color=COLORS["hover"],
                font=ctk.CTkFont(family="Arial", size=12),
                command=lambda o=op_id: self.show_operation(o),
            )
            btn.pack(pady=5)
            self.operation_buttons[op_id] = btn
            attach_tooltip(btn, tooltip)

    def show_operation(self, operation):
        for widget in self.left_panel.winfo_children():
            widget.destroy()

        self.current_operation = operation
        self.panels[operation].build(self.left_panel)
