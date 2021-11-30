import tkinter as tk
from enum import Enum

from PIL import Image, ImageDraw, ImageTk

from scipy.spatial import distance


class CreationState(Enum):
    BOARD = "board"
    LED = "led"


class ImagePane(tk.Frame):
    """This class consist the drawing functionalities

    TODO: Please move functionality in seperate model class!!!!

    :param self.img_path: is a relative path to the image which is loaded
    :type img_path: str
    :param self.master: is the master frame in which this frame is inserted
    :type master: tk.Frame
    :param self.polygon: is a reference for the current polygon
    :type polygon: Integer
    :param self.polygon_images: is a dict holding the drawn polygons.
        IMPORTANT: PLEASE DON'T DELETE THIS; OTHERWISE THE IMAGE IS OPTIMISED OUT
    :type polygon_images: Dictionary with ELements of type tk.Image
    :param self.canvas: is a tkinter canvas object
    :param self.points: are the currently displayed circles
    :param self.active_circle: is a reference as Integer to the currently selected circle
    :param self.anchor_points: are the anchor points for the polygon

    """

    def __init__(self, container):

        """

        :param container:
        """
        tk.Frame.__init__(self, container)
        self.master = container
        self.images = None
        self.img_path = None
        self.polygon = None
        self.polygon_images = {}
        self.canvas = tk.Canvas(container, height=400, width=400)
        self.canvas.pack()
        self.points = []
        self.leds = []
        self.anchor_points = []
        self.active_circle = 0
        self.change_state(CreationState.BOARD)
        self.but = tk.Button(container, text="Toggle ", command=self.toggle_state)
        self.but.pack()

    def choose_image(self, img_path):
        """
        opens an image and draws it on the canvas.
        The canvas is resized to the size of the image
        :param img_path: is a relative img path
        :return: void
        """
        self.anchor_points.clear()
        self.points.clear()
        self.img_path = img_path
        img = Image.open(self.img_path)
        self.images = [ImageTk.PhotoImage(img)]
        w = self.images[0].width()
        h = self.images[0].height()
        self.canvas.config(width=w, height=h)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.images[0])
        self.canvas.pack()

    def add_point(self, event):
        """

        :param event:
        :return:
        """
        circles = self.check_hovered(event.x, event.y)
        if not circles:
            if len(self.anchor_points) > 0:
                self.canvas.delete("poly")
            print(f"frame coordinates: {event.x}, {event.y}")
            self.anchor_points.append((event.x, event.y))
            anchor_point = self.create_circle(event.x, event.y, 10)
            self.points.append(anchor_point)
            self.update_polygon()
            self.active_circle = len(self.anchor_points) - 1
        else:
            self.active_circle = self.anchor_points.index(circles[0])



    def undo_point(self):
        if len(self.anchor_points) > 0:
            self.anchor_points.pop()
            point = self.points.pop()
            self.canvas.delete(point)
            self.update_polygon()



    def check_hovered(self, cx, cy):
        """
        helper function for
        :param cx:
        :param cy:
        :return:
        """
        circles = filter(lambda x: distance.euclidean((cx, cy), x) <= 10, self.anchor_points)
        return list(circles)

    def create_circle(self, x, y, r):
        """
        helper function for creating circle
        :param x: is the centered x
        :param y: is the centered y
        :param r: is the radius
        :return: a canvas object ref represented as Integer
        """
        x0 = x - r
        y0 = y - r
        x1 = x + r
        y1 = y + r
        return self.canvas.create_oval(x0, y0, x1, y1)

    def draw_circles(self):
        for point in self.anchor_points:
            anchor_point = self.create_circle(point[0], point[1], 10)
            self.points.append(anchor_point)

    def delete_circles(self):
        """
        deletes current displayed circles
        :return:
        """
        for ref in self.points:
            self.canvas.delete(ref)
        self.points = []

    def moving_anchor(self, event):
        print(f"hover cirle: {event.x} {event.y}")
        print(f"active cirle: {self.active_circle}")

        if self.current_state == CreationState.BOARD:
            anchor_point_ref = self.points[self.active_circle]
            self.anchor_points[self.active_circle] = (event.x, event.y)
            self.canvas.coords(anchor_point_ref, event.x - 10, event.y - 10, event.x + 10, event.y + 10)
            self.update_polygon()
        if self.current_state == CreationState.LED:
            pass


    def update_polygon(self):
        """
        Reads the current anchor_points and updates shape of polygon

        :return: void
        """
        if self.polygon is not None:
            self.canvas.delete(self.polygon)
        if len(self.anchor_points) > 1:
            points = [y for x in self.anchor_points for y in x]
            self.polygon = self.create_polygon(*points,
                                               has_index="board",
                                               outline='#f11',
                                               fill="red",
                                               width=2,
                                               tag="poly",
                                               alpha=0.5)
        else:
            self.polygon = None

    def create_polygon(self, *args, **kwargs):
        """
        creates an polygon using either PIL or tk.Canvas-

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

    def change_state(self, state: CreationState):
        """
        change state between Board and LED State
        :param state:
        :return:
        """
        self.current_state = state
        if self.current_state == CreationState.BOARD:
            self.__activate_board_state()
        if self.current_state == CreationState.LED:
            self.__activate_led_state()




    def remove_anchor_point(self, event):
        """
        removes an anchor_point
        :param event: is a Mouse event
        :return:
        """
        circles = self.check_hovered(event.x, event.y)
        if circles[0] is not None:
            index = self.anchor_points.index(circles[0])

            point = self.points[index]

            self.canvas.delete(point)
            self.anchor_points.remove(circles[0])
            self.points.remove(point)
            self.update_polygon()


    def __activate_board_state(self):
        """
        change all bindings to board state settings
        :return: void
        """
        self.canvas.bind("<Button-1>", self.add_point)
        self.canvas.bind("<Button-2>", self.remove_anchor_point)
        self.canvas.bind("<B1-Motion>", self.moving_anchor)
        self.master.bind("<Control-z>", lambda x: self.undo_point())
        self.draw_circles()

    def __activate_led_state(self):
        """
        change all bindings to led state settings
        :return: void
        """
        self.delete_circles()
        self.canvas.bind("<Button-1>", self.add_led)  #
        self.canvas.unbind("<B1-Motion>")



    def toggle_state(self):
        """
        This is just a helper function for toggling between the states.
        TODO:: DELETE THIS STUPID FUNCTION
        :return:
        """
        if self.current_state == CreationState.BOARD:
            self.change_state(CreationState.LED)
        else:
            self.change_state(CreationState.BOARD)

    def add_led(self, event):
        self.leds.append((event.x, event.y))
        self.create_circle(event.x, event.y, 20)
        circles = self.check_hovered(event.x, event.y)
        if not circles:
            self.create_circle(event.x, event.y, 20)
        else:
            self.active_circle = self.anchor_points.index(circles[0])







