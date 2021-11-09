import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class ImagePane(ttk.Labelframe):
    def __init__(self, container):
        super().__init__(container)
        self.img = None
        self.img_path = None
        self.canvas = None
        self.btn = tk.Button(self, text="open image", command=self.choose_image)

    def choose_image(self, img_path):
        self.img_path = img_path
        img = Image.open(self.img_path)
        self.img = ImageTk.PhotoImage(img)
        w = self.img.width()
        h = self.img.height()
        if self.canvas is None:
            self.canvas = tk.Canvas(self, height=h, width=w)
            self.canvas.pack()
        else:
            self.canvas.config(width=w, height=h)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img)
        self.pack()
