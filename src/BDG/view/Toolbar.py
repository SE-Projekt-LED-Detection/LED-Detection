import tkinter as tk
from tkinter import ttk

from BDG.coordinator.edit_handler import EditHandler
from BDG.view.ImagePane import ImagePane


class Toolbar(tk.Frame):
    """
    Responsible for the Radiobuttons which allow to switch between the CreationStates.
    The Radiobuttons update the tk.IntVar in the EditHandler.
    """
    def __init__(self, master, image_pane: ImagePane, handler: EditHandler):
        tk.Frame.__init__(self, master)
        self.image_pane = image_pane
        self.master = master
        self.handler = handler

        self.boardid_label = ttk.Label(self, text="Board id:")
        self.boardid_entry = ttk.Entry(self, textvariable=self.handler.board_id)

        handler.parent.on_update.get("on_update_image").append(lambda: self._make_boardid_entry_visible())

        r1 = ttk.Radiobutton(self, text="Place corner point", value=0, variable=self.handler.current_state,
                             command=self.image_pane.activate_board_state)
        r2 = ttk.Radiobutton(self, text="Place LED", value=1, variable=self.handler.current_state,
                             command=self.image_pane.activate_led_state)

        #btn_undo = ttk.Button(self, command=self.container.imagePane.undo_point, text="Undo")
        #btn_redo = ttk.Button(self, command=self.container.imagePane.redo_point, text="Redo")

        #btn_undo.grid(column=0, row=0, sticky=tk.W, padx=2)
        #btn_redo.grid(column=1, row=0, sticky=tk.W, padx=2)


        r1.grid(column=4, row=0, sticky=tk.W, padx=2)
        r2.grid(column=5, row=0, sticky=tk.W, padx=2)

    def _make_boardid_entry_visible(self):
        self.boardid_label.grid(column=2, row=0, sticky=tk.W, padx=2)
        self.boardid_entry.grid(column=3, row=0, sticky=tk.W, padx=2)
        self.handler.board_id.set(self.handler.board().id)  # Load boardid
