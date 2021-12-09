import tkinter as tk
from enum import Enum
from tkinter import ttk

from tkinter.filedialog import askopenfilename

from ImagePane import ImagePane
from src.BDG.Scrollable import ScrollbarFrame
from src.BDG.Toolbar import Toolbar


class ControlPane(tk.Frame):
    def __init__(self, container):
        tk.Frame.__init__(self, container)
        self.master = container
        menu = tk.Menu(self)
        self.master.config(menu=menu)
        fileMenu = tk.Menu(menu)
        menu.add_cascade(label="File", menu=fileMenu)
        editMenu = tk.Menu(menu)
        menu.add_cascade(label="Edit", menu=editMenu)

        self.imagePane = ImagePane(self.master)

        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_rowconfigure(1, weight=1)

        led_descriptions = ScrollbarFrame(self.master)
        led_descriptions.grid(column=4, row=1, sticky=tk.NSEW)
        bottom = tk.Label(led_descriptions.scrolled_frame, text="Fancy toolbar", background="blue")

        self.toolbar = Toolbar(self.master, self)

        #for i in range(30):
        #    ttk.Button(led_descriptions.scrolled_frame, text="I'm a button in the scrollable frame").grid(column=4, row=2+i)



        self.toolbar.grid(column=0, row=0, sticky=tk.W)
        bottom.grid(column=4, row=1, sticky=tk.NW)
        self.imagePane.grid(column=0, row=1, sticky=tk.NSEW)


        editMenu.add_command(label="Undo", command=self.imagePane.undo_point)
        editMenu.add_command(label="Redo", command=self.imagePane.redo_point)

        fileMenu.add_command(label="open", command=self.chooseImage)
        fileMenu.add_command(label="save", command=self.save_image)

        #menu.add_command(label="Toggle mode", command=self.imagePane.toggle_state)
        menu.add_command(label="Test", command=lambda: self.imagePane.choose_image(
            "/home/cj7/Desktop/LED-Detection/src/prototyping/resources/ref.jpg"))

    def chooseImage(self):
        path = askopenfilename()
        self.imagePane.choose_image(img_path=path)

    def save_image(self):
        print("Image saved")

    def exitProgram(self):
        exit()
