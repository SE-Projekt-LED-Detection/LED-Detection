import tkinter as tk
from enum import Enum
import numpy as np
from PIL import Image, ImageDraw, ImageTk

from scipy.spatial import distance

from src.BDG.model.CreationState import CreationState
from src.BDG.model.board_model import Board
from src.BDG.coordinator.edit_handler import EditHandler


class ImagePane(tk.Frame):
    """This class consist the drawing functionalities


    :param self.img_path: is a relative path to the image which is loaded
    :type img_path: str
    :param self.master: is the master frame in which this frame is inserted
    :type master: tk.Frame
    :param self.polygon: is a reference for the current polygon
    :type polygon: Integer
    :param self.polygon_images: is a dict holding the drawn polygons.
        IMPORTANT: PLEASE DON'T DELETE THIS; OTHERWISE THE IMAGE IS OPTIMISED OUT
    :type polygon_images: Dictionary with Elements of type tk.Image
    :param self.canvas: is a tkinter canvas object
    :param self.points: are the currently displayed circles
    :param self.active_circle: is a reference as Integer to the currently selected circle
    :param self.anchor_points: are the anchor points for the polygon

    """

    def __init__(self, master, container, handler: EditHandler):
        """
        Creates the image pane window.
        :param master: The root window.
        :param container: The window in which the ImagePane will be contained.
        :param handler: The EditHandler where the callable for the events should be registered.
        """
        tk.Frame.__init__(self, master)

        self.img = None
        self.handler = handler
        self.board = handler.board()
        self.master = master
        self.container = container
        self.image = None
        self.corner_references = []
        self.led_references = []
        self.current_state = tk.IntVar()
        self.canvas = tk.Canvas(master, height=720, width=1024)
        self.canvas.grid(row=1, column=0, sticky=tk.NSEW, columnspan=4)
        self.last_image_size = [0, 0]

        self.polygon = None
        self.polygon_images = {}
        self.leds_text_indices_references = []

        handler.parent.on_update.get("on_update_point").append(lambda: self.update_points())
        handler.parent.on_update.get("on_update_image").append(lambda: self.update_image())

        self.canvas.bind("<B1-Motion>", self.handler.moving_point)
        self.canvas.bind("<Button-3>", self.handler.delete_point)
        self.canvas.bind("<Button-2>", self.handler.delete_point)
        self.master.bind("<Control-z>", lambda x: self.handler.undo())
        self.master.bind("<Control-y>", lambda x: self.handler.redo())

        self.activate_board_state()

    def update_image(self):
        """
        Reloads the image of the current board object in the canvas.
        Automatically fits the image to the windows size by invoking a resize event.
        """
        self.update_board()
        self.img = Image.fromarray(self.board.image)
        self.image = ImageTk.PhotoImage(self.img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)
        self.canvas.bind("<Configure>", self.on_resize)

        # Initial resize of the image by calling event
        self.canvas.event_generate("<Configure>", width=self.canvas.winfo_width(), height=self.canvas.winfo_height())

    def update_points(self):
        """
        Removes and creates again all corner points and LEDs
        """
        # skip if there is no image
        if self.board.image is None:
            return

        # Cleanup canvas
        for ref in self.corner_references:
            self.canvas.delete(ref)

        for ref in self.led_references:
            self.canvas.delete(ref)

        # Draw new corners and LEDs
        if self.handler.is_state(CreationState.BOARD):
            for corner in self.board.corners:
                # error prevention if corner is empty
                self.draw_corner(corner)

        for led in self.board.led:
            self.draw_led(led.position, led.radius)

        self.update_polygon()
        self.update_led_indices()

    def on_resize(self, event):
        """
        Resizes the image in the canvas to fit the canvas while still having the same proportions.
        :param event:
        """
        basewidth = event.width
        baseheight = event.height
        self.img = Image.fromarray(self.board.image)
        scaling = (basewidth / float(self.img.size[0]))
        # hpercent = baseheight / float(self.img.size[1])
        new_height = int((float(self.img.size[1]) * float(scaling)))
        new_width = event.width

        # Too large for scaling fully in width -> scale height max
        if new_height > baseheight:
            new_height = baseheight
            scaling = baseheight / float(self.img.size[1])
            new_width = int((float(self.img.size[0]) * float(scaling)))

        self.handler.scaling = scaling

        if self.last_image_size[0] == 0:
            self.last_image_size = [new_width, new_height]

        scaled_image = self.img.resize((new_width, new_height), Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(scaled_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)
        self.update_points()

    def draw_corner(self, point):
        """
        Draws a corner at the given coordinates
        :param x: The x coordinate of the new corner
        :param y: The y coordinate of the new corner
        """
        point = np.array(point)
        reference = self.create_circle(point * self.handler.scaling, 10)
        self.corner_references.append(reference)

    def draw_led(self, position, radius):
        """
        Draws a LED at the given coordinates
        :param x: The x coordinate of the new LED
        :param y: The y coordinate of the new LED
        :param radius: The radius of the new LED
        """
        led_ref = self.create_circle(position * self.handler.scaling, radius)
        self.led_references.append(led_ref)

    def create_circle(self, position, r):
        """
        helper function for creating circle
        :param x: is the centered x
        :param y: is the centered y
        :param r: is the radius
        :return: a canvas object ref represented as Integer
        """
        p_0 = position - r
        p_1 = position + r
        return self.canvas.create_oval(p_0[0], p_0[1], p_1[0], p_1[1])

    def update_polygon(self):
        """
        Reads the current anchor_points and updates shape of polygon

        :return: void
        """

        if self.polygon is not None:
            self.canvas.delete(self.polygon)
        if len(self.board.corners) > 2:
            scaling = self.handler.scaling
            points = np.rint(np.array(self.board.corners) * scaling).astype(int)
            points = points.flatten().tolist()

            self.polygon = self.create_polygon(*points,
                                               has_index="board",
                                               outline='#f11',
                                               fill="red",
                                               width=2,
                                               tag="poly",
                                               alpha=0.5)
        else:
            self.polygon = None

    def update_led_indices(self):
        """
        Redraws the indices of the LEDs anew.
        """
        for index in self.leds_text_indices_references:
            self.canvas.delete(index)

        self.leds_text_indices_references.clear()

        i = 0
        for led in self.board.led:
            x = led.position[0] * self.handler.scaling + led.radius
            y = led.position[1] * self.handler.scaling + led.radius

            text = self.canvas.create_text(x, y, text=str(i))
            self.leds_text_indices_references.append(text)

            i += 1

    def create_polygon(self, *args, **kwargs):
        """
        Creates an polygon using either PIL or tk.Canvas-

        Because tk.Canvas doesn't support RGBA, the PIL lib is used to create an tkImage,
        which is added to the canvas
        :param args: is an even array of coordinates such as [x0, y0, x1, y1, ... , xn, yn]
        :param kwargs: are some named arguments which can be read in the ImageDraw Documentation. The fill keyword is required!

        :return: an canvas element
        """

        has_index = kwargs.pop("has_index") if "has_index" in kwargs else None
        if "alpha" in kwargs:
            if "fill" in kwargs:
                # Get and process the input data
                fill = self.master.winfo_rgb(kwargs.pop("fill")) \
                       + (int(kwargs.pop("alpha") * 255),)
                outline = kwargs.pop("outline") if "outline" in kwargs else None

                # We need to find a rectangle the polygon is inscribed in
                # (max(args[::2]), max(args[1::2])) are x and y of the bottom right point of this rectangle
                # and they also are the width and height of it respectively (the image will be inserted into
                # (0, 0) coords for simplicity)

                image = Image.new("RGBA", (max(args[::2]), max(args[1::2])))
                ImageDraw.Draw(image).polygon(args, fill=fill, outline=outline)
                # prevent the Image from being garbage-collected

                self.polygon_images[has_index] = ImageTk.PhotoImage(image)
                return self.canvas.create_image(0, 0, image=self.polygon_images[has_index],
                                                anchor="nw")  # insert the Image to the 0, 0 coords
            raise ValueError("fill color must be specified!")
        return self.canvas.create_polygon(*args, **kwargs)

    def activate_board_state(self):
        """
        Change all bindings to board state settings
        :return: void
        """
        self.canvas.bind("<Button-1>", self.handler.add_corner)
        self.canvas.unbind("<MouseWheel>")  # On Windows
        self.canvas.unbind("<Button-4>")  # On Linux
        self.canvas.unbind("<Button-5>")  # On Linux
        self.handler.parent.update_points()

    def activate_led_state(self):
        """
        Change all bindings to LED state settings
        :return: void
        """
        self.delete_circles()
        self.canvas.bind("<Button-1>", self.handler.add_led)
        self.canvas.bind("<MouseWheel>", self.handler.on_mousewheel)  # On Windows
        self.canvas.bind("<Button-4>", self.handler.on_mousewheel)  # On Linux
        self.canvas.bind("<Button-5>", self.handler.on_mousewheel)  # On Linux

    def update_board(self):
        """
        Sets the board object in self to the board object of the handler.
        """
        self.board = self.handler.board()

    def delete_circles(self):
        for ref in self.corner_references:
            self.canvas.delete(ref)
        """
        Sets the board object in self to the board object of the handler.
        """
        self.board = self.handler.board()

    def delete_circles(self):
        """
        Deletes the corner points bounding circles in the canvas.
        Used when the CreationState is switched to LED as the circles are then not visible anymore
        """
        for ref in self.corner_references:
            self.canvas.delete(ref)

