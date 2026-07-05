import tkinter as tk


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None

        self.widget.bind("<Enter>", self.show_tooltip, add="+")
        self.widget.bind("<Leave>", self.hide_tooltip, add="+")
        self.widget.bind("<ButtonPress>", self.hide_tooltip, add="+")

    def show_tooltip(self, _event=None):
        if self.tip_window or not self.text:
            return

        x = self.widget.winfo_rootx() + (self.widget.winfo_width() // 2)
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            tw,
            text=self.text,
            bg="#111111",
            fg="white",
            font=("Arial", 9),
            padx=6,
            pady=3,
        )
        label.pack()

    def hide_tooltip(self, _event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


def attach_tooltip(widget, text):
    widget.tooltip = ToolTip(widget, text)
