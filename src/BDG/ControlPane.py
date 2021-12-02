import tkinter as tk
from enum import Enum
from tkinter import ttk

from tkinter.filedialog import askopenfilename
from ImagePane import ImagePane





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

        toolbar = tk.Frame(self.master, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        names = tk.Frame(self.master, relief=tk.RAISED)
        names.pack(side=tk.RIGHT, fill=tk.X)
        bottom = tk.Label(names, text="Fancy toolbar")
        bottom.pack(side=tk.RIGHT)


        #self.window = tk.PanedWindow(orient=tk.HORIZONTAL)
        #self.window.pack(fill="both", expand="True")
        #self.window.add(self)


        #self.window.add(bottom)

        v = tk.IntVar()
        r1 = tk.Radiobutton(toolbar, text="Place corner point", value=1, variable=v)
        r2 = tk.Radiobutton(toolbar, text="Place LED", value=2, variable=v)
        r1.pack(side=tk.LEFT, fill=None, expand=False)
        r2.pack(side=tk.LEFT, fill=None, expand=False)
        #self.window.add(r1)
        #self.window.add(r2)

        self.imagePane = ImagePane(self.master)
        self.imagePane.pack(side=tk.LEFT)



        editMenu.add_command(label="Undo", command=self.imagePane.undo_point)
        editMenu.add_command(label="Redo", command=self.imagePane.redo_point)

        fileMenu.add_command(label="open", command=self.chooseImage)
        fileMenu.add_command(label="save", command=self.save_image)

        menu.add_command(label="Toggle mode", command=self.imagePane.toggle_state)
        menu.add_command(label="Test", command=lambda: self.imagePane.choose_image(
            "/home/cj7/Desktop/LED-Detection/src/prototyping/resources/ref.jpg"))

    def chooseImage(self):
        path = askopenfilename()
        self.imagePane.choose_image(img_path=path)

    def save_image(self):
        print("Image saved")

    def exitProgram(self):
        exit()
