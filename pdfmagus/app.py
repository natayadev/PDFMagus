import os
import tkinter as tk
from datetime import datetime
from tkinter import ttk

import customtkinter as ctk
from PIL import Image, ImageTk

from pdfmagus.reading.history import ReadingHistory
from pdfmagus.tabs.convert_tab import ConvertTab
from pdfmagus.tabs.edit_tab import EditTab
from pdfmagus.tabs.logs_tab import LogsTab
from pdfmagus.theme import COLORS, FONTS, load_icons
from pdfmagus.widgets.tooltip import attach_tooltip

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class PDFMagus(ctk.CTk):
    def __init__(self, base_dir):
        super().__init__()

        self.base_dir = base_dir
        self._drag_start_x = 0
        self._drag_start_y = 0

        self.title("PDFMagus - PDF Manager")
        self.geometry("1400x900")
        self.resizable(True, True)
        self.state("zoomed")
        self.configure(fg_color=COLORS["white"])
        self.overrideredirect(True)

        self.icons = load_icons()

        mango_img = Image.open(os.path.join(self.base_dir, "icon.ico"))
        mango_img = mango_img.resize((60, 60), Image.Resampling.LANCZOS)
        self.mango_photo = ImageTk.PhotoImage(mango_img)
        self.iconphoto(True, self.mango_photo)

        self._configure_notebook_style()

        notebook_container = tk.Frame(self, bg=COLORS["background"])
        notebook_container.pack(fill="both", expand=True, padx=0, pady=0)

        self._build_top_bar(notebook_container)

        self.notebook = ttk.Notebook(notebook_container)
        self.notebook.pack(fill="both", expand=True, padx=0, pady=0)

        reading_history = ReadingHistory(
            os.path.join(self.base_dir, "reader_history.json"), self.log_event
        )

        self.edit_tab = EditTab(self.notebook, self.icons, self.log_event, reading_history)
        self.convert_tab = ConvertTab(self.notebook, self.icons, self.log_event)
        self.logs_tab = LogsTab(self.notebook, self.clear_logs)

        self.edit_tab.load_last_reading_session()

        self.log_event("Application started")

    def _configure_notebook_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "TNotebook", background=COLORS["primary"], foreground=COLORS["black"], borderwidth=0
        )
        style.configure(
            "TNotebook.Tab",
            background=COLORS["white"],
            foreground=COLORS["black"],
            borderwidth=1,
            padding=[25, 10],
            focuscolor="none",
            font=FONTS["tab_label"],
            relief="raised",
            anchor="center",
            lightcolor=COLORS["white"],
            darkcolor=COLORS["white"],
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", COLORS["white"])],
            foreground=[("selected", COLORS["black"])],
            padding=[("selected", [25, 14])],
            relief=[("selected", "ridge")],
        )

    def _build_top_bar(self, parent):
        top_bar = tk.Frame(parent, bg=COLORS["background"], height=40)
        top_bar.pack(fill="x", side="top", pady=(2, 0))
        top_bar.pack_propagate(False)

        top_bar.bind("<Button-1>", self.start_drag)
        top_bar.bind("<B1-Motion>", self.on_drag)

        window_buttons_frame = tk.Frame(top_bar, bg=COLORS["background"])
        window_buttons_frame.pack(side="right", padx=10, pady=5)

        btn_minimize = ctk.CTkButton(
            window_buttons_frame,
            text="",
            image=self.icons["minimize"],
            width=30,
            height=30,
            fg_color=COLORS["background"],
            hover_color=COLORS["primary_hover"],
            command=self.minimize_window,
        )
        btn_minimize.pack(side="left", padx=2)
        attach_tooltip(btn_minimize, "Minimize")

        btn_maximize = ctk.CTkButton(
            window_buttons_frame,
            text="",
            image=self.icons["maximize"],
            width=30,
            height=30,
            fg_color=COLORS["background"],
            hover_color=COLORS["primary_hover"],
            command=self.toggle_maximize,
        )
        btn_maximize.pack(side="left", padx=2)
        attach_tooltip(btn_maximize, "Maximize")

        btn_close = ctk.CTkButton(
            window_buttons_frame,
            text="",
            image=self.icons["close"],
            width=30,
            height=30,
            fg_color=COLORS["background"],
            hover_color=COLORS["danger_hover"],
            command=self.on_app_close,
        )
        btn_close.pack(side="left", padx=2)
        attach_tooltip(btn_close, "Close")

    def log_event(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"
        if hasattr(self, "logs_tab"):
            self.logs_tab.append_line(log_line)

    def clear_logs(self):
        if hasattr(self, "logs_tab"):
            self.logs_tab.clear()
            self.log_event("Logs cleared")

    def start_drag(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def on_drag(self, event):
        x = self.winfo_x() + event.x - self._drag_start_x
        y = self.winfo_y() + event.y - self._drag_start_y
        self.geometry(f"+{x}+{y}")

    def minimize_window(self):
        self.overrideredirect(False)
        self.iconify()
        self._map_bind_id = self.bind("<Map>", self._restore_after_minimize, add="+")

    def _restore_after_minimize(self, _event=None):
        self.overrideredirect(True)
        if hasattr(self, "_map_bind_id") and self._map_bind_id:
            self.unbind("<Map>", self._map_bind_id)
            self._map_bind_id = None

    def toggle_maximize(self):
        if self.state() == "zoomed":
            self.state("normal")
        else:
            self.state("zoomed")

    def on_app_close(self):
        try:
            self.edit_tab.persist_on_exit()
            self.log_event("Application closed - state saved")
        except Exception as e:
            self.log_event(f"Error saving state: {e}")

        self.quit()
