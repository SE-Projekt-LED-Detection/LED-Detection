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

    TODO: Please move functionality in separate model class!!!!

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

        :param container:
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
        self.update_board()
        self.img = Image.fromarray(self.board.image)
        self.image = ImageTk.PhotoImage(self.img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)
        self.canvas.bind("<Configure>", self.on_resize)

        # Initial resize of the image by calling event
        self.canvas.event_generate("<Configure>", width=self.canvas.winfo_width(), height=self.canvas.winfo_height())

    def update_points(self):
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
        reference = self.create_circle(point * self.handler.scaling, 10)
        self.corner_references.append(reference)

    def draw_led(self, position, radius):
        """

        :param position: is the position
        :param radius: is the radius
        :returns:
        """
        led_ref = self.create_circle(position * self.handler.scaling, radius)
        self.led_references.append(led_ref)

    def create_circle(self, position, r):
        """
        helper function for creating circle
        :param point: np.array
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
        if self.board.corners.shape[0] > 1:
            scaling = self.handler.scaling
            points = self.board.corners * scaling


            # points = [y for x in map(lambda p: [round(p[0] * self.handler.scaling), round(p[1] * self.handler.scaling)], self.board.corners) for y in x]

            self.polygon = self.create_polygon(points,
                                               has_index="board",
                                               outline='#f11',
                                               fill="red",
                                               width=2,
                                               tag="poly",
                                               alpha=0.5)
        else:
            self.polygon = None

    def update_led_indices(self):

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
        creates an polygon using either PIL or tk.Canvas-

        Because tk.Canvas doesn't support RGBA, the PIL lib is used to create an tkImage,
        which is added to the canvas
        :param args[0] is a numpy array like this [[x_0, y_0],[x_1, y_1]]
        :param kwargs: are some named arguments which can be read in the ImageDraw Documentation. The fill keyword is required!

        :return: an canvas element
        """

        points = args[0].astype(int)
        max_vals = np.amax(points, axis=0)
        points = points.T
        points = points.flatten().tolist()

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

                image = Image.new("RGBA", (max_vals[0], max_vals[1]))
                ImageDraw.Draw(image).polygon(points, fill=fill, outline=outline)
                # prevent the Image from being garbage-collected

                self.polygon_images[has_index] = ImageTk.PhotoImage(image)
                return self.canvas.create_image(0, 0, image=self.polygon_images[has_index],
                                                anchor="nw")  # insert the Image to the 0, 0 coords
            raise ValueError("fill color must be specified!")
        return self.canvas.create_polygon(points, **kwargs)

    def activate_board_state(self):
        """
        change all bindings to board state settings
        :return: void
        """
        self.canvas.bind("<Button-1>", self.handler.add_corner)
        self.canvas.unbind("<MouseWheel>")  # On Windows
        self.canvas.unbind("<Button-4>")  # On Linux
        self.canvas.unbind("<Button-5>")  # On Linux
        self.handler.parent.update_points()

    def activate_led_state(self):
        """
        change all bindings to led state settings
        :return: void
        """
        self.delete_circles()
        self.canvas.bind("<Button-1>", self.handler.add_led)
        self.canvas.bind("<MouseWheel>", self.handler.on_mousewheel)  # On Windows
        self.canvas.bind("<Button-4>", self.handler.on_mousewheel)  # On Linux
        self.canvas.bind("<Button-5>", self.handler.on_mousewheel)  # On Linux

    def update_board(self):
        self.board = self.handler.board()


    def delete_circles(self):
        for ref in self.corner_references:
            self.canvas.delete(ref)

