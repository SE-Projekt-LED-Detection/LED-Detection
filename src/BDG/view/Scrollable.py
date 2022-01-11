import tkinter as tk
from tkinter import ttk


# https://stackoverflow.com/questions/3085696/adding-a-scrollbar-to-a-group-of-widgets-in-tkinter/3092341
from src.BDG.coordinator.edit_handler import EditHandler
from src.BDG.coordinator.event_handler import EventHandler
from src.BDG.view.LedDisplay import LedDisplay


class ScrollbarFrame(tk.Frame):
    """
    Extends class tk.Frame to support a scrollable Frame
    This class is independent from the widgets to be scrolled and
    can be used to replace a standard tk.Frame
    """

    def __init__(self, parent, edit_handler: EditHandler, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)

        # The Scrollbar, layout to the right
        self.edit_handler = edit_handler
        vsb = tk.Scrollbar(self, orient="vertical")
        vsb.pack(side="right", fill="y")

        # The Canvas which supports the Scrollbar Interface, layout to the left
        self.canvas = tk.Canvas(self, borderwidth=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        # Bind the Scrollbar to the self.canvas Scrollbar Interface
        self.canvas.configure(yscrollcommand=vsb.set)
        vsb.configure(command=self.canvas.yview)

        # The Frame to be scrolled, layout into the canvas
        # All widgets to be scrolled have to use this Frame as parent
        self.scrolled_frame = tk.Frame(self.canvas, background=self.canvas.cget('bg'))
        self.windows_item = self.canvas.create_window((4, 4), window=self.scrolled_frame, anchor="nw")

        # Configures the scrollregion of the Canvas dynamically
        self.scrolled_frame.bind("<Configure>", self.on_configure)

        self.descriptions = []

        # Register events
        self.edit_handler.parent.on_update.get("on_update_point").append(lambda: self.redraw_led_description())

    def on_configure(self, event):
        """Set the scroll region to encompass the scrolled frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def redraw_led_description(self):
        board = self.edit_handler.board()
        if len(board.led) == len(self.descriptions):
            # Count of LEDs has not been changed, meaning no changes to be made
            return

        # Remove old descriptions, only if actually removed in board
        for (led, des) in self.descriptions:
            if led not in board.led:
                des.destroy()
                self.descriptions.remove((led, des))

        # Add new descriptions
        for led in board.led:
            if led not in map(lambda x: x[0], self.descriptions):
                single_description = LedDisplay(self.scrolled_frame, 0, led)
                self.descriptions.append((led, single_description))

        for i in range(len(self.descriptions)):
            self.descriptions[i][1].update_number(i)





