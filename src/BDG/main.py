import tkinter as tk
import os
from ControlPane import ControlPane


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('Board Description Generator')
        self.geometry('300x120')

        self.resizable(True, True)


if __name__ == "__main__":
    app = App()
    ControlPane(app)
    app.mainloop()