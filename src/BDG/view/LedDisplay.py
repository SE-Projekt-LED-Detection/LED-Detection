from tkinter.ttk import Frame
import tkinter as tk
from tkinter import ttk

from BDG.model.board_model import Led


class LedDisplay(Frame):
    """
    A class which contains the widgets to enter the necessary meta information about LEDs.
    Will be grided into a Scrollable
    """

    def __init__(self, parent, index, led: Led, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)

        self.led = led
        self.grid(column=4, row=2 + index, sticky=tk.W, pady=10)

        self.single_description = ttk.Frame(self)
        self.single_description.grid(column=4, row=2 + index, sticky=tk.W, pady=10)

        self.number = tk.StringVar()
        self.number.set("LED " + str(index))
        self.number_label = ttk.Label(self.single_description, textvariable=self.number)
        self.number_label.grid(column=0, row=0, sticky=tk.W)

        ttk.Label(self.single_description, text="Name/Function").grid(column=0, row=1, sticky=tk.W)
        self.name = tk.StringVar()
        self.name.set(led.id)
        self.name.trace("w", lambda name, i, mode, sv=self.name: self.__on_name_changed(sv))
        ttk.Entry(self.single_description, textvariable=self.name).grid(column=1, row=1)

        ttk.Label(self.single_description, text="Possible Colors").grid(column=0, row=2, sticky=tk.W)
        self.red = tk.IntVar()
        self.yellow = tk.IntVar()
        self.green = tk.IntVar()
        checkbox_frame = ttk.Frame(self.single_description)
        red_check = tk.Checkbutton(checkbox_frame, text="Red", variable=self.red)
        yellow_check = tk.Checkbutton(checkbox_frame, text="Yellow", variable=self.yellow)
        green_check = tk.Checkbutton(checkbox_frame, text="Green", variable=self.green)

        # Set default values
        self.red.set(1 if "red" in led.colors else 0)
        self.yellow.set(1 if "yellow" in led.colors else 0)
        self.green.set(1 if "green" in led.colors else 0)

        # Change events
        self.red.trace("w", lambda name, i, mode, int_var=self.red, color="red": self.__on_color_changed(int_var, color))
        self.yellow.trace("w", lambda name, i, mode, int_var=self.yellow, color="yellow": self.__on_color_changed(int_var, color))
        self.green.trace("w", lambda name, i, mode, int_var=self.green, color="green": self.__on_color_changed(int_var, color))

        red_check.grid(column=1, row=0, sticky=tk.W)
        yellow_check.grid(column=2, row=0, sticky=tk.W)
        green_check.grid(column=3, row=0, sticky=tk.W)
        checkbox_frame.grid(column=1, row=2)

    def __on_color_changed(self, var: tk.IntVar, color: str):
        """
        Called when the checked state of a checkbox changed an hence the possible colors of the LED.
        Appends or removes the color in the list of the LED.
        :param var: The tk.IntVar which is traced.
        :param color: The color which the CheckBox of the tk.Invar represents.
        """
        if var.get() == 1:
            self.led.colors.append(color)
        else:
            self.led.colors.remove(color)

    def __on_name_changed(self, var):
        """
        Called when the text of the entry box is changed by tracing the tk.StringVar.
        Sets the id attribute in the LED
        :param var: The traced tk.StringVar
        """
        self.led.id = var.get()

    def update_number(self, new_number):
        self.number.set("LED " + str(new_number))
        self.grid(column=4, row=2 + new_number, sticky=tk.W, pady=10)

