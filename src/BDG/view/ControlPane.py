import tkinter as tk



from src.BDG.utils.json_util import from_json
from src.BDG.view.ImagePane import ImagePane
from src.BDG.view.Scrollable import ScrollbarFrame
from src.BDG.view.Toolbar import Toolbar
from src.BDG.model.board_model import Board
from src.BDG.coordinator.event_handler import EventHandler



class ControlPane(tk.Frame):
    def __init__(self, container):
        tk.Frame.__init__(self, container)
        self.handler = EventHandler()
        self.master = container

        #self.imagePane = ImagePane(self.master, self, self.handler.edit_handler)
        self.__init_menu()

        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_rowconfigure(1, weight=1)

        self.led_descriptions = ScrollbarFrame(self.master)
        self.led_descriptions.grid(column=4, row=1, sticky=tk.NSEW)

        self.toolbar = Toolbar(self.master, self)

        self.toolbar.grid(column=0, row=0, sticky=tk.W)
        #self.imagePane.grid(column=0, row=1, sticky=tk.NSEW)

    def save_image(self):
        board = self.imagePane.get_board()

    def exitProgram(self):
        exit()

    def export_board(self) -> Board:
        """TODO!!!!

        Returns:
            Board: [description]
        """
        return Board()

    def __init_menu(self):
        menu = tk.Menu(self)
        self.master.config(menu=menu)
        self.__init_filemenu(menu)
        self.__init_editmenu(menu)
        #menu.add_command(label="Test", command=lambda: self.imagePane.choose_image("/home/cj7/Desktop/LED-Detection/src/prototyping/resources/ref.jpg"))
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
        #editMenu.add_command(label="Undo", command=self.imagePane.undo_point)
        #editMenu.add_command(label="Redo", command=self.imagePane.redo_point)
