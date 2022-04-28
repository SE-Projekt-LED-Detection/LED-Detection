import tkinter as tk

from BDG.coordinator.event_handler import EventHandler
from BDG.model.board_model import Board
from BDG.view.ImagePane import ImagePane
from BDG.view.Scrollable import ScrollbarFrame
from BDG.view.Toolbar import Toolbar


class ControlPane(tk.Frame):
    def __init__(self, container):
        tk.Frame.__init__(self, container)
        self.handler = EventHandler()
        self.master = container

        self.imagePane = ImagePane(self.master, self, self.handler.edit_handler)
        self.__init_menu()

        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_rowconfigure(1, weight=1)

        self.led_descriptions = ScrollbarFrame(self.master, self.handler.edit_handler)
        self.led_descriptions.grid(column=4, row=1, sticky=tk.NSEW)

        self.toolbar = Toolbar(self.master, self.imagePane, self.handler.edit_handler)

        self.toolbar.grid(column=0, row=0, sticky=tk.W)
        self.imagePane.grid(column=0, row=1, sticky=tk.NSEW)

    def exitProgram(self):
        exit()

    def __init_menu(self):
        menu = tk.Menu(self)
        self.master.config(menu=menu)
        self.__init_filemenu(menu)
        self.__init_editmenu(menu)
        return menu

    def __init_filemenu(self, menu):
        fileMenu = tk.Menu(menu)
        handler = self.handler.file_handler
        menu.add_cascade(label="File", menu=fileMenu)
        fileMenu.add_command(label="open", command=handler.load)
        fileMenu.add_command(label="save", command=handler.save)

    def __init_editmenu(self, menu):
        editMenu = tk.Menu(menu)
        menu.add_cascade(label="Edit", menu=editMenu)
        editMenu.add_command(label="Undo", command=lambda: self.handler.edit_handler.undo())
        editMenu.add_command(label="Redo", command=lambda: self.handler.edit_handler.redo())
