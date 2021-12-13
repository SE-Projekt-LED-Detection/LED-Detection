from tkinter.ttk import Frame
import tkinter as tk
from tkinter import ttk


class LedDisplay(Frame):
    """
    A frame which contains entry fields for the description of a LED.
    Contains an entry for name/function, checkboxes for possible colors and a label which display the index of the LED.
    """

    def __init__(self, parent, index, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)

        self.grid(column=4, row=2 + index, sticky=tk.W, pady=10)

        self.single_description = ttk.Frame(self)
        self.single_description.grid(column=4, row=2 + index, sticky=tk.W, pady=10)
        self.number = tk.StringVar()
        self.number.set("LED " + str(index))
        self.number_label = ttk.Label(self.single_description, textvariable=self.number)
        self.number_label.grid(column=0, row=0, sticky=tk.W)
        ttk.Label(self.single_description, text="Name/Function").grid(column=0, row=1, sticky=tk.W)
        self.name = tk.StringVar()
        ttk.Entry(self.single_description, textvariable=self.name).grid(column=1, row=1)

        ttk.Label(self.single_description, text="Possible Colors").grid(column=0, row=2, sticky=tk.W)
        self.red = tk.IntVar()
        self.yellow = tk.IntVar()
        self.green = tk.IntVar()
        checkbox_frame = ttk.Frame(self.single_description)
        red_check = tk.Checkbutton(checkbox_frame, text="Red", variable=self.red)
        yellow_check = tk.Checkbutton(checkbox_frame, text="Yellow", variable=self.yellow)
        green_check = tk.Checkbutton(checkbox_frame, text="Green", variable=self.green)
        red_check.grid(column=1, row=0, sticky=tk.W)
        yellow_check.grid(column=2, row=0, sticky=tk.W)
        green_check.grid(column=3, row=0, sticky=tk.W)
        checkbox_frame.grid(column=1, row=2)

    def update_number(self, new_number):
        """
        Updates the number of the LED which will be displayed in the list.
        :param new_number: THe new number of the LED
        """
        self.number.set("LED " + str(new_number))
        self.grid(column=4, row=2 + new_number, sticky=tk.W, pady=10)

    def get_color_list(self):
        """
        Returns a list with the colors where the checkbox in the list are checked.
        :return: The list with the checked colors
        """
        colors = []
        if self.red.get() == 1:
            colors.append("red")
        if self.yellow.get() == 1:
            colors.append("yellow")
        if self.green.get() == 1:
            colors.append("green")

        return colors

    def get_name(self):
        """
        Returns the name of the LED which the user typed into the according entry.
        :return: The name of the LED as string
        """
        return self.name.get()
