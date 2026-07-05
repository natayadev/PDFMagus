import tkinter as tk


class ZoomSlider(tk.Frame):
    TRACK_LEFT = 5
    TRACK_RIGHT = 145
    THUMB_RADIUS = 6

    def __init__(self, parent, colors, min_value, max_value, initial_value, on_change):
        super().__init__(parent, bg=colors["white"], height=40, width=150)
        self.pack_propagate(False)

        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.on_change = on_change

        self.canvas = tk.Canvas(
            self,
            width=150,
            height=25,
            bg=colors["white"],
            highlightthickness=0,
            cursor="hand2",
        )
        self.canvas.pack(fill="both", expand=True)

        self.canvas.create_line(
            self.TRACK_LEFT, 12, self.TRACK_RIGHT, 12, fill=colors["gray_medium"], width=4
        )

        thumb_x = self._value_to_x(initial_value)
        self.thumb = self.canvas.create_oval(
            thumb_x - self.THUMB_RADIUS,
            6,
            thumb_x + self.THUMB_RADIUS,
            18,
            fill=colors["primary"],
            outline=colors["primary"],
        )

        self.canvas.bind("<Button-1>", self._on_pointer_event)
        self.canvas.bind("<B1-Motion>", self._on_pointer_event)
        self.canvas.bind("<ButtonRelease-1>", self._on_pointer_event)

    def _value_to_x(self, value):
        span = self.max_value - self.min_value
        ratio = (value - self.min_value) / span
        return self.TRACK_LEFT + ratio * (self.TRACK_RIGHT - self.TRACK_LEFT)

    def _on_pointer_event(self, event):
        x = max(self.TRACK_LEFT, min(event.x, self.TRACK_RIGHT))
        span = self.TRACK_RIGHT - self.TRACK_LEFT
        ratio = (x - self.TRACK_LEFT) / span
        self.value = round(self.min_value + ratio * (self.max_value - self.min_value), 2)

        self.canvas.coords(
            self.thumb,
            x - self.THUMB_RADIUS,
            6,
            x + self.THUMB_RADIUS,
            18,
        )

        self.on_change(self.value)
