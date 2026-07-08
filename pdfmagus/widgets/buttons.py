import customtkinter as ctk

from pdfmagus.theme import COLORS
from pdfmagus.widgets.tooltip import attach_tooltip


def icon_button(parent, icon, command, tooltip=None, size=40, **kwargs):
    """Icon-only button using the app's standard neutral/hover styling."""
    btn = ctk.CTkButton(
        parent,
        text="",
        image=icon,
        width=size,
        height=size,
        fg_color=COLORS["white"],
        hover_color=COLORS["hover"],
        command=command,
        **kwargs,
    )
    if tooltip:
        attach_tooltip(btn, tooltip)
    return btn


def primary_button(parent, text, command, width=150, height=40, font=None, **kwargs):
    """Solid brand-colored action button (e.g. 'Select File', 'Add PDFs')."""
    return ctk.CTkButton(
        parent,
        text=text,
        width=width,
        height=height,
        fg_color=COLORS["primary"],
        hover_color=COLORS["primary_hover"],
        font=font or ctk.CTkFont(family="Arial", size=11),
        command=command,
        **kwargs,
    )


def run_button(parent, text, command, width=200, height=45):
    """The large bold call-to-action button used at the bottom of operation panels."""
    return ctk.CTkButton(
        parent,
        text=text,
        width=width,
        height=height,
        fg_color=COLORS["primary"],
        hover_color=COLORS["primary_hover"],
        font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
        command=command,
    )


def secondary_button(parent, text, command, width=80, height=35, hover_color=None, font=None, **kwargs):
    """Small neutral utility button (e.g. 'Browse', 'Remove', reorder arrows)."""
    return ctk.CTkButton(
        parent,
        text=text,
        width=width,
        height=height,
        fg_color=COLORS["white"],
        hover_color=hover_color or COLORS["hover"],
        font=font or ctk.CTkFont(family="Arial", size=10),
        command=command,
        **kwargs,
    )


class ToggleableIconButton:
    """Icon button whose enabled state swaps between the theme icons
    ``<icon_name>`` and ``<icon_name>_disabled``, keeping visuals and
    interactivity in sync in one place instead of at every call site."""

    def __init__(self, parent, icons, icon_name, command, tooltip=None, size=40, enabled=False):
        self.icons = icons
        self.icon_name = icon_name
        self.button = ctk.CTkButton(
            parent,
            text="",
            image=icons[icon_name if enabled else f"{icon_name}_disabled"],
            width=size,
            height=size,
            fg_color=COLORS["white"],
            hover_color=COLORS["hover"],
            command=command,
            state="normal" if enabled else "disabled",
        )
        if tooltip:
            attach_tooltip(self.button, tooltip)

    def set_enabled(self, enabled):
        self.button.configure(
            state="normal" if enabled else "disabled",
            image=self.icons[self.icon_name if enabled else f"{self.icon_name}_disabled"],
        )

    def pack(self, **kwargs):
        self.button.pack(**kwargs)
        return self
