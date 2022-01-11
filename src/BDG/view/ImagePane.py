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

    #
    #
    #
    #
    #
    #
    #
    # # The below code is legacy code, the logic will be in another class
    #
    # def choose_image(self, img):
    #     """
    #     opens an image and draws it on the canvas.
    #     The canvas is resized to the size of the image
    #     :param img: is either a relative img path or a numpy array
    #     :return: void
    #     """
    #     self.anchor_points.clear()
    #     self.points.clear()
    #     if isinstance(img, np.ndarray):
    #         self.img = Image.fromarray(img)
    #         self.images = [ImageTk.PhotoImage(self.img)]
    #     elif isinstance(img, str):
    #         self.img_path = img
    #         self.img = Image.open(self.img_path)
    #         self.images = [ImageTk.PhotoImage(self.img)]
    #     else:
    #         raise TypeError
    #     self.canvas.create_image(0, 0, anchor=tk.NW, image=self.images[0])
    #     self.canvas.bind("<Configure>", self.on_resize)
    #
    #     # Initial resize of the image by calling event
    #     self.canvas.event_generate("<Configure>", width=self.canvas.winfo_width(), height=self.canvas.winfo_height())
    #
    # def update_points_scaling(self, new_width, new_height):
    #     """
    #     Moves the LEDs and anchor points of the image to be relatively at the same position on teh resized image
    #     with new_width and new_height
    #     :param new_width: The new width of the resized image
    #     :param new_height: The new height of the resized image
    #     """
    #     self.undone_points = list(map(lambda x: [int(x[0] * self.scaling_w), int(x[1] * self.scaling_h)], self.undone_points))
    #     self.undone_leds = list(map(lambda x: [int(x[0] * self.scaling_w), int(x[1] * self.scaling_h), x[2]], self.undone_leds))
    #
    #     scaling_x = new_width / self.last_image_size[0]
    #     scaling_y = new_height / self.last_image_size[1]
    #     last_image_diagonal = pow(pow(self.last_image_size[0], 2) + pow(self.last_image_size[1], 2), 0.5)
    #     new_image_diagonal = pow(pow(new_width, 2) + pow(new_height, 2), 0.5)
    #     diagonal_scaling = new_image_diagonal / last_image_diagonal
    #
    #     for i in range(len(self.leds)):
    #         led = self.leds.pop(0)
    #         self.canvas.delete(self.leds_references.pop(0))
    #         self.add_led_by_coordinates(round(led[0] * scaling_x), round(led[1] * scaling_y), round(led[2] * diagonal_scaling))
    #
    #     for i in range(len(self.anchor_points)):
    #         anchor = self.anchor_points.pop(0)
    #         if self.is_state(CreationState.BOARD):
    #             self.canvas.delete(self.points.pop(0))
    #         self.add_point_by_coordinates(round(anchor[0] * scaling_x), round(anchor[1] * scaling_y))
    #
    #     self.last_image_size = [new_width, new_height]
    #
    # def add_point_by_coordinates(self, x, y):
    #     """
    #     Creates a anchor point at the given coordinates.
    #     Only 4 anchor points can exist at the same time.
    #     :param x: The x coordinate of the anchor point.
    #     :param y: The y coordinates of the anchor point.
    #     """
    #     circles = self.check_hovered(x, y)
    #     if not circles:
    #         if len(self.anchor_points) >= 4:
    #             return
    #
    #         if len(self.anchor_points) > 0:
    #             self.canvas.delete("poly")
    #         print(f"frame coordinates: {x}, {y}")
    #         self.anchor_points.append((x, y))
    #         anchor_point = self.create_circle(x, y, 10)
    #         self.points.append(anchor_point)
    #         self.update_polygon()
    #         self.active_circle = len(self.anchor_points) - 1
    #     else:
    #         self.active_circle = self.anchor_points.index(circles[0])
    #
    # def add_led_by_coordinates(self, x, y, radius=20):
    #     """
    #     Creates a LED at the given coordinates.
    #     :param radius: The radius of the led. Default value 20
    #     :param x: The x coordinates of the LED.
    #     :param y: The y coordinate of the LED.
    #     """
    #     circles = self.check_hovered(x, y)
    #     if not circles:
    #         led_ref = self.create_circle(x, y, radius)
    #         index = len(self.leds)
    #         self.leds.append((x, y, radius))
    #         self.leds_references.append(led_ref)
    #         self.active_circle = len(self.leds) - 1
    #         self.container.led_descriptions.add_led_description(index)
    #         self.update_led_indices()
    #     else:
    #         self.active_circle = self.leds.index(circles[0])
    #
    # def redo_point(self):
    #     """
    #     Redo the last LED/point if available.
    #     """
    #     if self.is_state(CreationState.BOARD):
    #         if len(self.undone_points) > 0 and len(self.anchor_points) < 4:
    #             point = self.undone_points.pop()
    #             self.add_point_by_coordinates(point[0], point[1])
    #     if self.is_state(CreationState.LED):
    #         if len(self.undone_leds) > 0:
    #             led = self.undone_leds.pop()
    #             self.add_led_by_coordinates(led[0], led[1])
    #
    # def undo_point(self):
    #     """
    #     Undo the last set LED or Anchor point.
    #     The undone led/point is saved in a list for the redo operation.
    #     """
    #     if self.is_state(CreationState.BOARD):
    #         if len(self.anchor_points) > 0:
    #             coordinates_point = self.anchor_points.pop()
    #             point = self.points.pop()
    #             self.undone_points.append(coordinates_point)
    #             self.canvas.delete(point)
    #             self.update_polygon()
    #     if self.is_state(CreationState.LED):
    #         if len(self.leds) > 0:
    #             led = self.leds.pop()
    #             self.undone_leds.append(led)
    #             ref = self.leds_references.pop()
    #             self.canvas.delete(ref)
    #             self.container.led_descriptions.remove_led_description(len(self.leds))
    #             self.update_led_indices()

    # def draw_circles(self):
    #     for point in self.anchor_points:
    #         anchor_point = self.create_circle(point[0], point[1], 10)
    #         self.points.append(anchor_point)
    #
    # def delete_circles(self):
    #     """
    #     deletes current displayed circles
    #     :return:
    #     """
    #     for ref in self.points:
    #         self.canvas.delete(ref)
    #         self.points = []
    #
    # def moving_anchor(self, event):
    #     """
    #     Moves the currently selected anchor point or LED
    #     :param event:
    #     """
    #     print(f"hover circle: {event.x} {event.y}")
    #     print(f"active circle: {self.active_circle}")
    #
    #     # Moving outside the image?
    #     if event.x > self.last_image_size[0] or event.y > self.last_image_size[1]\
    #             or event.x < 0 or event.y < 0:
    #         return
    #
    #     if self.is_state(CreationState.BOARD):
    #         anchor_point_ref = self.points[self.active_circle]
    #         self.anchor_points[self.active_circle] = (event.x, event.y)
    #         self.canvas.coords(anchor_point_ref, event.x - 10, event.y - 10, event.x + 10, event.y + 10)
    #         self.update_polygon()
    #     if self.is_state(CreationState.LED):
    #         led_ref = self.leds_references[self.active_circle]
    #         radius = self.leds[self.active_circle][2]
    #         self.leds[self.active_circle] = (event.x, event.y, radius)
    #         self.canvas.coords(led_ref, event.x - radius, event.y - radius, event.x + radius, event.y + radius)
    #         self.update_led_indices()

    # """
    # def on_mousewheel(self, event):
    #
    #     count = 0
    #     if event.num == 5 or event.delta == -120:
    #         count = -1
    #     if event.num == 4 or event.delta == 120:
    #         count = 1
    #
    #     circles = self.check_hovered(event.x, event.y)
    #     if circles:
    #
    #         active_led = circles[0]
    #         index = self.leds.index(active_led)
    #         led_ref = self.leds_references[index]
    #
    #         radius = active_led[2] + count
    #         self.leds[index] = (active_led[0], active_led[1], radius)
    #         self.canvas.coords(led_ref, active_led[0] - radius, active_led[1] - radius, active_led[0] + radius, active_led[1] + radius)
    #         self.update_led_indices()
    # """
    #
    #
