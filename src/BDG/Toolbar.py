import tkinter as tk
from tkinter import ttk


class Toolbar(tk.Frame):
    def __init__(self, master, container):
        tk.Frame.__init__(self, master)
        self.master = master
        self.container = container

        v = tk.IntVar()
        r1 = ttk.Radiobutton(self, text="Place corner point", value=1, variable=v)
        r2 = ttk.Radiobutton(self, text="Place LED", value=2, variable=v)

        btn_undo = ttk.Button(self, command=self.container.imagePane.undo_point, text="Undo")
        btn_redo = ttk.Button(self, command=self.container.imagePane.redo_point, text="Redo")

        btn_undo.grid(column=0, row=0, sticky=tk.W, padx=2)
        btn_redo.grid(column=1, row=0, sticky=tk.W, padx=2)
        r1.grid(column=2, row=0, sticky=tk.W, padx=2)
        r2.grid(column=3, row=0, sticky=tk.W, padx=2)
