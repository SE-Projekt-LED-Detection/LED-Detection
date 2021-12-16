import tkinter as tk


from tkinter.filedialog import askopenfilename


from src.BDG.utils.json_util import from_json
from src.BDG.view.ImagePane import ImagePane
from src.BDG.view.Scrollable import ScrollbarFrame
from src.BDG.view.Toolbar import Toolbar
from src.BDG.model.board_model import Board

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

        self.imagePane = ImagePane(self.master, self)

        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_rowconfigure(1, weight=1)

        self.led_descriptions = ScrollbarFrame(self.master)
        self.led_descriptions.grid(column=4, row=1, sticky=tk.NSEW)

        self.toolbar = Toolbar(self.master, self)



        self.toolbar.grid(column=0, row=0, sticky=tk.W)
        self.imagePane.grid(column=0, row=1, sticky=tk.NSEW)


        editMenu.add_command(label="Undo", command=self.imagePane.undo_point)
        editMenu.add_command(label="Redo", command=self.imagePane.redo_point)

        fileMenu.add_command(label="open", command=self.chooseImage)
        fileMenu.add_command(label="save", command=self.save_image)

        menu.add_command(label="Test", command=lambda: self.imagePane.choose_image(
            "/home/cj7/Desktop/LED-Detection/src/prototyping/resources/ref.jpg"))

    def chooseImage(self):
        path = askopenfilename()
        if path.lower().endswith(".jpg", ".png", "jpeg"):
            self.imagePane.choose_image(img=path)
        elif path.lower().endswith(".json"):
            board = from_json(path)
            self.imagePane.load_board(board)
        else:
            print("Wrong filetype!!!") # TODO: make this a little bit better...

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



