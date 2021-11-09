import tkinter as tk
from tkinter import ttk

from tkinter.filedialog import askopenfilename
from ImagePane import ImagePane


class ControlPane(ttk.Labelframe):
    def __init__(self, container):
        super().__init__(container)
        self.btn = tk.Button(self, text="open image", command=self.chooseImage)
        self.imagePane = ImagePane(container)
        self.btn.pack()
        self.pack()


    def chooseImage(self):
        path = askopenfilename()
        self.imagePane.choose_image(img_path=path)
        self.pack()
