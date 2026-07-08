import gc
import io
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

import customtkinter as ctk
import fitz
from PIL import Image, ImageTk
from tkfontawesome import icon_to_image

from pdfmagus.ocr import service as ocr_service
from pdfmagus.theme import COLORS
from pdfmagus.widgets.buttons import icon_button, ToggleableIconButton
from pdfmagus.widgets.tooltip import attach_tooltip
from pdfmagus.widgets.zoom_slider import ZoomSlider

ANNOTATION_MODES = {"highlight", "underline", "strikeout", "squiggly"}

HIGHLIGHT_COLORS = [
    ("Pink", (1, 0.6, 0.73), "#FFB3BA"),
    ("Yellow", (1, 1, 0.6), "#FFFF99"),
    ("Green", (0.6, 1, 0.6), "#99FF99"),
    ("Blue", (0.6, 1, 1), "#99FFFF"),
    ("Magenta", (1, 0.6, 1), "#FF99FF"),
]


class EditTab(tk.Frame):
    def __init__(self, notebook, icons, log_event, reading_history):
        super().__init__(notebook, bg=COLORS["white"])
        notebook.add(self, text="Edit")

        self.icons = icons
        self.log_event = log_event
        self.reading_history = reading_history

        self.edit_doc = None
        self.current_pdf_path = None
        self.edit_page_num = 0
        self.edit_zoom = 0.9
        self.edit_highlights = []
        self.selected_edit_color = (1, 0.6, 0.73)
        self.edit_drag_start = None
        self.annot_mode = "highlight"
        self.reader_mode_enabled = False

        self._build_ui()
        self.set_annot_mode("highlight")
        self.update_reader_mode_button_state()
        self.canvas.after(100, self.show_placeholder_edit)

    def _build_ui(self):
        middle_section = tk.Frame(self, bg=COLORS["white"])
        middle_section.pack(fill="both", expand=True, padx=10, pady=5)

        self._build_left_panel(middle_section)
        self._build_canvas_panel(middle_section)
        self._build_bottom_section()

    def _build_left_panel(self, parent):
        left_panel = tk.Frame(parent, bg=COLORS["white"])
        left_panel.pack(side="left", fill="y", padx=10, pady=10)

        icon_button(left_panel, self.icons["open_pdf"], command=self.open_pdf_edit, tooltip="Open PDF").pack(pady=5)

        self.btn_save = ToggleableIconButton(
            left_panel, self.icons, "save_pdf", command=self.save_highlighted_edit, tooltip="Save PDF"
        )
        self.btn_save.pack(pady=5)

        self.btn_ocr = ToggleableIconButton(
            left_panel, self.icons, "ocr", command=self.extract_text_ocr, tooltip="Extract text (OCR)"
        )
        self.btn_ocr.pack(pady=5)

        self.btn_export = ToggleableIconButton(
            left_panel, self.icons, "export", command=self.export_highlights_edit, tooltip="Export"
        )
        self.btn_export.pack(pady=5)

        self.btn_undo = ToggleableIconButton(
            left_panel, self.icons, "undo", command=self.undo_edit, tooltip="Undo"
        )
        self.btn_undo.pack(pady=5)

        self.annot_mode_icons = {
            "highlight": self.icons["highlight_mode"],
            "underline": self.icons["underline_mode"],
            "strikeout": self.icons["strikeout_mode"],
            "squiggly": self.icons["underline_mode"],
        }

        self.btn_annot_mode = icon_button(
            left_panel,
            self.annot_mode_icons["highlight"],
            command=self.show_annot_mode_menu,
            tooltip="Annotation mode",
        )
        self.btn_annot_mode.pack(pady=5)

        self.annot_mode_menu = tk.Menu(
            self,
            tearoff=0,
            bg=COLORS["white"],
            fg=COLORS["primary"],
            activebackground=COLORS["hover"],
            activeforeground=COLORS["primary"],
        )
        self.annot_mode_menu.add_command(label="Highlight", command=lambda: self.set_annot_mode("highlight"))
        self.annot_mode_menu.add_command(label="Underline", command=lambda: self.set_annot_mode("underline"))
        self.annot_mode_menu.add_command(label="Strikeout", command=lambda: self.set_annot_mode("strikeout"))
        self.annot_mode_menu.add_command(label="Squiggly", command=lambda: self.set_annot_mode("squiggly"))

        tk.Frame(left_panel, bg=COLORS["white"]).pack(fill="x", pady=10)

        color_frame = tk.Frame(left_panel, bg=COLORS["white"])
        color_frame.pack(pady=5)

        self.color_buttons = {}
        for name, rgb, hex_color in HIGHLIGHT_COLORS:
            btn = ctk.CTkButton(
                color_frame,
                text="",
                width=30,
                height=30,
                fg_color=hex_color,
                hover_color=hex_color,
                corner_radius=15,
                command=lambda c=rgb: self.select_edit_color(c),
            )
            btn.pack(pady=5)
            self.color_buttons[rgb] = btn
            attach_tooltip(btn, name)

        self.color_buttons[(1, 0.6, 0.73)].configure(border_width=2, border_color=COLORS["border"])

        tk.Frame(left_panel, bg=COLORS["white"]).pack(fill="x", pady=10)

        self.btn_clear = ToggleableIconButton(
            left_panel, self.icons, "clear", command=self.clear_highlights_edit, tooltip="Clear"
        )
        self.btn_clear.pack(pady=5)

    def _build_canvas_panel(self, parent):
        canvas_panel = tk.Frame(parent, bg=COLORS["white"])
        canvas_panel.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        canvas_container = tk.Frame(canvas_panel, bg=COLORS["white"])
        canvas_container.pack(fill="both", expand=True)

        vsb = tk.Scrollbar(canvas_container, orient="vertical")
        vsb.pack(side="right", fill="y")
        hsb = tk.Scrollbar(canvas_container, orient="horizontal")
        hsb.pack(side="bottom", fill="x")

        self.canvas = tk.Canvas(
            canvas_container, bg=COLORS["canvas"], yscrollcommand=vsb.set, xscrollcommand=hsb.set
        )
        self.canvas.pack(side="left", fill="both", expand=True)
        vsb.configure(command=self.canvas.yview)
        hsb.configure(command=self.canvas.xview)

        self.canvas.bind("<MouseWheel>", self.on_edit_mouse_wheel)
        self.canvas.bind("<Left>", lambda e: self.prev_edit_page())
        self.canvas.bind("<Right>", lambda e: self.next_edit_page())
        self.canvas.bind("<Control-z>", lambda e: self.undo_edit())
        self.canvas.bind("<Control-s>", lambda e: self.save_highlighted_edit())
        self.canvas.focus_set()

        self.canvas.bind("<ButtonPress-1>", self.on_edit_highlight_start)
        self.canvas.bind("<B1-Motion>", self.on_edit_highlight_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_edit_highlight_end)

    def _build_bottom_section(self):
        bottom_section = tk.Frame(self, bg=COLORS["white"])
        bottom_section.pack(fill="x", padx=10, pady=5)

        self.btn_prev = ToggleableIconButton(
            bottom_section, self.icons, "prev_page", command=self.prev_edit_page, tooltip="Previous page"
        )
        self.btn_prev.pack(side="left", padx=5)

        self.lbl_page_info = ctk.CTkLabel(
            bottom_section,
            text="0/0",
            font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
            text_color=COLORS["black"],
        )
        self.lbl_page_info.pack(side="left", padx=20)

        self.btn_next = ToggleableIconButton(
            bottom_section, self.icons, "next_page", command=self.next_edit_page, tooltip="Next page"
        )
        self.btn_next.pack(side="left", padx=5)

        center_frame = tk.Frame(bottom_section, bg=COLORS["white"])
        center_frame.pack(side="left", fill="x", expand=True)

        self.btn_reader_mode = ctk.CTkButton(
            center_frame,
            text="▶ Reader Mode",
            width=130,
            height=36,
            fg_color=COLORS["white"],
            hover_color=COLORS["hover"],
            text_color=COLORS["black"],
            font=ctk.CTkFont(family="Arial", size=11, weight="bold"),
            command=self.toggle_reader_mode,
            state="disabled",
        )
        self.btn_reader_mode.pack(anchor="center", padx=15)

        self.zoom_slider = ZoomSlider(
            bottom_section,
            COLORS,
            min_value=0.5,
            max_value=2.0,
            initial_value=0.9,
            on_change=self.on_edit_zoom_change,
        )
        self.zoom_slider.pack(side="right", padx=5)

        self.lbl_zoom = tk.Label(
            bottom_section, text="90%", bg=COLORS["white"], fg=COLORS["black"], font=("Arial", 12, "bold")
        )
        self.lbl_zoom.pack(side="right", padx=10)

    def open_pdf_edit(self):
        try:
            file_path = filedialog.askopenfilename(
                title="Select PDF",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            )
            if not file_path or not os.path.exists(file_path):
                return

            if self.edit_doc:
                self.edit_doc.close()
            gc.collect()

            self.edit_doc = fitz.open(file_path)
            self.edit_highlights = []
            self.current_pdf_path = file_path

            num_pages = len(self.edit_doc)
            saved_page_num = self.reading_history.get_saved_page(file_path)
            self.edit_page_num = min(max(saved_page_num, 0), max(num_pages - 1, 0))

            file_name = os.path.basename(file_path)
            self.log_event(f"PDF opened in Edit: {file_name} ({num_pages} pages)")

            self.reading_history.register_session(file_path, self.edit_page_num)
            self.update_reader_mode_button_state()

            self.render_edit_page()
        except Exception as e:
            self.log_event(f"Error opening PDF in Edit: {e}")
            messagebox.showerror("Error", f"Could not open the PDF:\n{e}")

    def render_edit_page(self):
        if not self.edit_doc:
            self.show_placeholder_edit()
            return
        try:
            page = self.edit_doc[self.edit_page_num]
            mat = fitz.Matrix(self.edit_zoom * 2, self.edit_zoom * 2)
            pix = page.get_pixmap(matrix=mat)
            img = Image.open(io.BytesIO(pix.tobytes("ppm")))
            self.edit_photo = ImageTk.PhotoImage(img)

            self.canvas.delete("all")

            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            img_width = self.edit_photo.width()
            img_height = self.edit_photo.height()
            x = max(0, (canvas_width - img_width) // 2)
            y = max(0, (canvas_height - img_height) // 2)

            self.canvas.create_image(x, y, anchor="nw", image=self.edit_photo, tags="pdf_image")
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            self.canvas.tag_lower("pdf_image")

            self.redraw_edit_highlights()

            total_pages = len(self.edit_doc)
            self.lbl_page_info.configure(text=f"Page: {self.edit_page_num + 1} / {total_pages}")

            self.btn_prev.set_enabled(self.edit_page_num > 0)
            self.btn_next.set_enabled(self.edit_page_num < total_pages - 1)
            self.btn_ocr.set_enabled(True)

            if self.current_pdf_path:
                self.reading_history.register_session(self.current_pdf_path, self.edit_page_num)
        except Exception as e:
            messagebox.showerror("Error", f"Render error: {e}")

    def show_placeholder_edit(self):
        self.canvas.delete("all")
        self.canvas.update_idletasks()

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1:
            canvas_width = 800
        if canvas_height <= 1:
            canvas_height = 600

        self.placeholder_icon = icon_to_image("wand-magic-sparkles", fill="#555555", scale_to_width=20)

        self.canvas.create_image(
            canvas_width // 2,
            canvas_height // 2 - 15,
            image=self.placeholder_icon,
            anchor="center",
            tags="placeholder",
        )

        self.canvas.create_text(
            canvas_width // 2,
            canvas_height // 2 + 10,
            text="Open a PDF to see the magic...",
            font=("Arial", 16, "bold"),
            fill="#666666",
            justify="center",
            anchor="center",
            tags="placeholder",
        )

        self.lbl_page_info.configure(text="0/0")
        self.btn_prev.set_enabled(False)
        self.btn_next.set_enabled(False)
        self.btn_ocr.set_enabled(False)

    def _draw_annotation(self, x1, y1, x2, y2, color, mode):
        if mode == "highlight":
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, stipple="gray50", outline="", tags="highlight")
        elif mode == "underline":
            line_y = y2 - 2
            self.canvas.create_line(x1, line_y, x2, line_y, fill=color, width=3, tags="highlight")
        elif mode == "strikeout":
            line_y = (y1 + y2) / 2
            self.canvas.create_line(x1, line_y, x2, line_y, fill=color, width=3, tags="highlight")
        elif mode == "squiggly":
            line_y = y2 - 2
            step = 3
            x_pos = x1
            y_offset = 0
            while x_pos < x2:
                next_x = min(x_pos + step, x2)
                y_offset = 2 if y_offset == 0 else 0
                self.canvas.create_line(
                    x_pos, line_y + y_offset, next_x, line_y + (2 - y_offset), fill=color, width=2, tags="highlight"
                )
                x_pos = next_x

    def redraw_edit_highlights(self):
        try:
            self.canvas.delete("highlight")
            if len(self.edit_highlights) <= self.edit_page_num:
                return

            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            img_width = self.edit_photo.width() if hasattr(self, "edit_photo") else 0
            img_height = self.edit_photo.height() if hasattr(self, "edit_photo") else 0
            offset_x = max(0, (canvas_width - img_width) // 2)
            offset_y = max(0, (canvas_height - img_height) // 2)

            render_scale = max(self.edit_zoom * 2, 0.1)
            for highlight in self.edit_highlights[self.edit_page_num]:
                rect = highlight["rect"]
                x1 = rect.x0 * render_scale + offset_x
                y1 = rect.y0 * render_scale + offset_y
                x2 = rect.x1 * render_scale + offset_x
                y2 = rect.y1 * render_scale + offset_y
                self._draw_annotation(x1, y1, x2, y2, highlight["color"], highlight.get("mode", "highlight"))

            self.canvas.tag_raise("highlight")
        except Exception:
            pass

    def prev_edit_page(self):
        if self.edit_doc and self.edit_page_num > 0:
            self.edit_page_num -= 1
            self.render_edit_page()
            if self.current_pdf_path:
                self.reading_history.register_session(self.current_pdf_path, self.edit_page_num)

    def next_edit_page(self):
        if self.edit_doc and self.edit_page_num < len(self.edit_doc) - 1:
            self.edit_page_num += 1
            self.render_edit_page()
            if self.current_pdf_path:
                self.reading_history.register_session(self.current_pdf_path, self.edit_page_num)

    def on_edit_zoom_change(self, value):
        self.edit_zoom = max(float(value), 0.1)
        self.lbl_zoom.configure(text=f"{int(self.edit_zoom * 100)}%")
        if self.edit_doc:
            self.render_edit_page()

    def on_edit_mouse_wheel(self, event):
        if not self.edit_doc:
            return
        if event.delta < 0:
            self.next_edit_page()
        else:
            self.prev_edit_page()
        return "break"

    def on_edit_highlight_start(self, event):
        self.edit_drag_start = (event.x, event.y)
        self.canvas.delete("selection_rect")

    def on_edit_highlight_drag(self, event):
        if self.edit_drag_start:
            self.canvas.delete("selection_rect")
            self.canvas.create_rectangle(
                self.edit_drag_start[0],
                self.edit_drag_start[1],
                event.x,
                event.y,
                outline=COLORS["selection"],
                width=2,
                dash=(4, 4),
                tags="selection_rect",
            )

    def on_edit_highlight_end(self, event):
        if not self.edit_doc or not self.edit_drag_start:
            return

        try:
            x1, y1 = self.edit_drag_start
            x2, y2 = event.x, event.y

            if x1 > x2:
                x1, x2 = x2, x1
            if y1 > y2:
                y1, y2 = y2, y1

            if abs(x2 - x1) < 10 or abs(y2 - y1) < 5:
                return

            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            img_width = self.edit_photo.width() if hasattr(self, "edit_photo") else 0
            img_height = self.edit_photo.height() if hasattr(self, "edit_photo") else 0
            offset_x = max(0, (canvas_width - img_width) // 2)
            offset_y = max(0, (canvas_height - img_height) // 2)

            render_scale = max(self.edit_zoom * 2, 0.1)

            pdf_x1 = (x1 - offset_x) / render_scale
            pdf_y1 = (y1 - offset_y) / render_scale
            pdf_x2 = (x2 - offset_x) / render_scale
            pdf_y2 = (y2 - offset_y) / render_scale

            page = self.edit_doc[self.edit_page_num]
            rect = fitz.Rect(pdf_x1, pdf_y1, pdf_x2, pdf_y2)
            words = page.get_text("words")
            found_words = [fitz.Rect(word[:4]) for word in words if fitz.Rect(word[:4]).intersects(rect)]

            r, g, b = self.selected_edit_color
            hex_color = f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"

            if len(self.edit_highlights) <= self.edit_page_num:
                self.edit_highlights.extend([[] for _ in range(self.edit_page_num + 1 - len(self.edit_highlights))])

            if found_words:
                for word_rect in found_words:
                    wx1 = word_rect.x0 * render_scale + offset_x
                    wy1 = word_rect.y0 * render_scale + offset_y
                    wx2 = word_rect.x1 * render_scale + offset_x
                    wy2 = word_rect.y1 * render_scale + offset_y

                    self._draw_annotation(wx1, wy1, wx2, wy2, hex_color, self.annot_mode)
                    self.edit_highlights[self.edit_page_num].append(
                        {"rect": word_rect, "color": hex_color, "mode": self.annot_mode}
                    )
            else:
                self._draw_annotation(x1, y1, x2, y2, hex_color, self.annot_mode)
                self.edit_highlights[self.edit_page_num].append(
                    {"rect": rect, "color": hex_color, "mode": self.annot_mode}
                )

            self.canvas.tag_raise("highlight")

            if self.edit_highlights[self.edit_page_num]:
                self.btn_save.set_enabled(True)
                self.btn_export.set_enabled(True)
                self.btn_clear.set_enabled(True)
                self.btn_undo.set_enabled(True)
        except Exception as e:
            messagebox.showerror("Error", f"Highlight error: {e}")
        finally:
            self.edit_drag_start = None
            self.canvas.delete("selection_rect")

    def select_edit_color(self, color_rgb):
        self.selected_edit_color = color_rgb
        for color, btn in self.color_buttons.items():
            if color == color_rgb:
                btn.configure(border_width=2, border_color=COLORS["border"])
            else:
                btn.configure(border_width=0)

    def show_annot_mode_menu(self):
        try:
            x = self.btn_annot_mode.winfo_rootx()
            y = self.btn_annot_mode.winfo_rooty() + self.btn_annot_mode.winfo_height()
            self.annot_mode_menu.tk_popup(x, y)
        finally:
            self.annot_mode_menu.grab_release()

    def set_annot_mode(self, mode):
        if mode not in ANNOTATION_MODES:
            mode = "highlight"

        self.annot_mode = mode
        self.btn_annot_mode.configure(image=self.annot_mode_icons.get(mode, self.annot_mode_icons["highlight"]))
        self.log_event(f"Annotation mode changed to: {mode.upper()}")

    def undo_edit(self):
        if not self.edit_doc or not self.edit_highlights:
            return

        if len(self.edit_highlights) > self.edit_page_num and self.edit_highlights[self.edit_page_num]:
            self.edit_highlights[self.edit_page_num].pop()
            self.render_edit_page()

            if not self.edit_highlights[self.edit_page_num]:
                self.btn_save.set_enabled(False)
                self.btn_export.set_enabled(False)
                self.btn_clear.set_enabled(False)
                self.btn_undo.set_enabled(False)

    def clear_highlights_edit(self):
        if not self.edit_doc:
            return
        if messagebox.askyesno("Confirm", "Clear all highlights on this page?"):
            if len(self.edit_highlights) > self.edit_page_num:
                self.edit_highlights[self.edit_page_num] = []
            self.render_edit_page()

            self.btn_save.set_enabled(False)
            self.btn_export.set_enabled(False)
            self.btn_clear.set_enabled(False)
            self.btn_undo.set_enabled(False)

    def save_highlighted_edit(self):
        if not self.edit_doc or not self.edit_highlights or all(len(h) == 0 for h in self.edit_highlights):
            messagebox.showwarning("Warning", "No highlights to save.")
            return

        try:
            base_name = os.path.splitext(os.path.basename(self.edit_doc.name or "document"))[0]
            output_path = filedialog.asksaveasfilename(
                title="Save highlighted PDF",
                defaultextension=".pdf",
                initialfile=f"{base_name} - highlighted.pdf",
                filetypes=[("PDF files", "*.pdf")],
            )
            if not output_path:
                return

            doc_copy = fitz.open(self.edit_doc.name)

            for page_num, highlights in enumerate(self.edit_highlights):
                if not highlights or page_num >= len(doc_copy):
                    continue
                page = doc_copy[page_num]
                for highlight in highlights:
                    words = page.get_text("words")
                    found_words = [
                        fitz.Rect(w[:4]) for w in words if fitz.Rect(w[:4]).intersects(highlight["rect"])
                    ]
                    if not found_words:
                        continue
                    try:
                        hex_color = highlight["color"].lstrip("#")
                        r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (0, 2, 4))

                        mode = highlight.get("mode")
                        if mode == "underline":
                            annot = page.add_underline_annot(found_words)
                            annot.set_opacity(0.6)
                        elif mode == "strikeout":
                            annot = page.add_strikeout_annot(found_words)
                            annot.set_opacity(0.6)
                        elif mode == "squiggly":
                            annot = page.add_squiggly_annot(found_words)
                            annot.set_opacity(0.6)
                        else:
                            annot = page.add_highlight_annot(found_words)
                            annot.set_opacity(0.5)

                        annot.set_colors(stroke=(r, g, b))
                        annot.update()
                    except Exception as e:
                        self.log_event(f"Error applying annotation: {e}")

            for page_num in range(len(doc_copy)):
                doc_copy[page_num].clean_contents()

            doc_copy.save(output_path, garbage=4, deflate=True)
            doc_copy.close()
            self.log_event(f"PDF saved with annotations: {os.path.basename(output_path)}")
            messagebox.showinfo("Success", f"PDF saved to:\n{output_path}")
        except Exception as e:
            self.log_event(f"Error saving annotated PDF: {e}")
            messagebox.showerror("Error", f"Error saving: {e}")

    def export_highlights_edit(self):
        if not self.edit_doc or not self.edit_highlights or all(len(h) == 0 for h in self.edit_highlights):
            messagebox.showinfo("No highlights", "There is no highlighted text to export.")
            return

        try:
            base_name = os.path.splitext(os.path.basename(self.edit_doc.name or "document"))[0]
            output_path = filedialog.asksaveasfilename(
                title="Save notes",
                defaultextension=".txt",
                initialfile=f"{base_name} - notes.txt",
                filetypes=[("Text files", "*.txt")],
            )
            if not output_path:
                return

            all_highlights = []
            for page_num, highlights in enumerate(self.edit_highlights):
                if not highlights:
                    continue
                page = self.edit_doc[page_num]
                page_highlights = []
                for highlight in highlights:
                    words = page.get_text("words")
                    text_parts = [w[4] for w in words if fitz.Rect(w[:4]).intersects(highlight["rect"])]
                    if text_parts:
                        page_highlights.append(" ".join(text_parts))
                if page_highlights:
                    all_highlights.append({"page": page_num + 1, "highlights": page_highlights})

            if not all_highlights:
                messagebox.showinfo("No highlights", "There is no text to export.")
                return

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"NOTES FROM: {os.path.basename(self.edit_doc.name or 'document')}\n")
                f.write("=" * 60 + "\n\n")
                for item in all_highlights:
                    f.write(f"PAGE {item['page']}\n" + "-" * 40 + "\n")
                    for highlight in item["highlights"]:
                        f.write(f"- {highlight}\n")
                    f.write("\n")

            total_fragments = sum(len(item["highlights"]) for item in all_highlights)
            self.log_event(f"Notes exported: {os.path.basename(output_path)}")
            messagebox.showinfo(
                "Success", f"Notes exported:\n{output_path}\n\nTotal: {total_fragments} fragments"
            )
        except Exception as e:
            self.log_event(f"Error exporting notes: {e}")
            messagebox.showerror("Error", f"Error exporting: {e}")

    def toggle_reader_mode(self):
        has_doc_open = bool(self.edit_doc and self.current_pdf_path and os.path.exists(self.current_pdf_path))
        if not has_doc_open:
            self.update_reader_mode_button_state()
            return

        self.reader_mode_enabled = not self.reader_mode_enabled
        state_text = "enabled" if self.reader_mode_enabled else "disabled"
        self.log_event(f"Reader mode {state_text}")
        self.update_reader_mode_button_state()

    def update_reader_mode_button_state(self):
        has_doc_open = bool(self.edit_doc and self.current_pdf_path and os.path.exists(self.current_pdf_path))
        is_active = bool(self.reader_mode_enabled)

        if not has_doc_open:
            self.reader_mode_enabled = False
            self.btn_reader_mode.configure(
                state="disabled",
                text="▶ Reader Mode",
                text_color=COLORS["gray_medium"],
                font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
            )
            return

        if is_active:
            self.btn_reader_mode.configure(
                state="normal",
                text="■ Stop Reader",
                text_color=COLORS["black"],
                font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
            )
        else:
            self.btn_reader_mode.configure(
                state="normal",
                text="▶ Reader Mode",
                text_color=COLORS["gray_medium"],
                font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
            )

    def load_last_reading_session(self):
        self.reading_history.load_last_session()
        self.update_reader_mode_button_state()

    def persist_on_exit(self):
        if self.edit_doc and self.current_pdf_path:
            self.reading_history.register_session(self.current_pdf_path, self.edit_page_num)

    def extract_text_ocr(self):
        if not self.edit_doc:
            messagebox.showwarning("Warning", "Open a PDF first")
            return

        if not ocr_service.is_available():
            messagebox.showerror(
                "Error", "The 'pytesseract' library is not installed.\nTry: pip install pytesseract"
            )
            return

        self.log_event(f"Starting OCR on page {self.edit_page_num + 1}...")

        thread = threading.Thread(target=self._run_ocr_thread)
        thread.daemon = True
        thread.start()

    def _run_ocr_thread(self):
        try:
            page = self.edit_doc[self.edit_page_num]
            mat = fitz.Matrix(2.5, 2.5)
            pix = page.get_pixmap(matrix=mat)
            img = Image.open(io.BytesIO(pix.tobytes("ppm")))

            if not ocr_service.ensure_tesseract_found():
                self.after(
                    0,
                    lambda: messagebox.showerror(
                        "Tesseract not found",
                        "The Tesseract OCR engine was not found.\n"
                        "Install it from: https://github.com/UB-Mannheim/tesseract/wiki",
                    ),
                )
                return

            ocr_text = ocr_service.run_ocr(img)

            if not ocr_text.strip():
                self.after(0, lambda: messagebox.showinfo("OCR", "No text detected on this page."))
                return

            self.after(0, lambda: self._show_ocr_results(ocr_text))
        except Exception as e:
            message = str(e)
            self.after(0, lambda: messagebox.showerror("OCR Error", message))
            self.log_event(f"OCR error: {message}")

    def _show_ocr_results(self, text):
        results_win = ctk.CTkToplevel(self)
        results_win.title(f"OCR text - Page {self.edit_page_num + 1}")
        results_win.geometry("500x400")
        results_win.attributes("-topmost", True)

        text_area = scrolledtext.ScrolledText(results_win, wrap=tk.WORD, font=("Consolas", 10))
        text_area.pack(fill="both", expand=True, padx=10, pady=10)
        text_area.insert("end", text)

        def copy_to_clipboard():
            self.clipboard_clear()
            self.clipboard_append(text)
            messagebox.showinfo("Copied", "Text copied to clipboard")

        ctk.CTkButton(
            results_win,
            text="Copy text",
            command=copy_to_clipboard,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
        ).pack(pady=10)
        self.log_event("OCR completed successfully")
