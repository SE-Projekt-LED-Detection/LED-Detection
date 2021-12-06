import tkinter as tk
from enum import Enum

from PIL import Image, ImageDraw, ImageTk

from scipy.spatial import distance


class CreationState(Enum):
    """
    The current placement mode. If it is BOARD, an anchor point is placed on left mouse click,
    if it is LED a LED is placed.
    """
    BOARD = "board"
    LED = "led"


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

    def __init__(self, container):

        """

        :param container:
        """
        tk.Frame.__init__(self, container)
        self.master = container
        self.images = None
        self.img = None
        self.img_path = None
        self.polygon = None
        self.polygon_images = {}
        self.canvas = tk.Canvas(container, height=720, width=1024)
        self.canvas.pack(fill="both", expand="True")
        self.points = []
        self.leds = []
        self.leds_references = []
        self.undone_points = []
        self.undone_leds = []
        self.anchor_points = []
        self.active_circle = 0
        self.change_state(CreationState.BOARD)
        self.scaling_w = 1
        self.scaling_h = 1
        self.last_image_size = [0, 0]

        self.master.bind("<Control-z>", lambda x: self.undo_point())
        self.master.bind("<Control-y>", lambda x: self.redo_point())
        self.master.bind("<t>", lambda x: self.toggle_state())

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
        self.img = Image.open(self.img_path)
        self.images = [ImageTk.PhotoImage(self.img)]
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.images[0])
        self.canvas.pack(fill="both", expand="True")
        self.canvas.bind("<Configure>", self.on_resize)

        # Initial resize of the image by calling event
        self.canvas.event_generate("<Configure>", width=self.canvas.winfo_width(), height=self.canvas.winfo_height())

    def on_resize(self, event):
        """
        Resizes the image in the canvas to fit the canvas while still having the same proportions.
        :param event:
        """
        basewidth = event.width
        baseheight = event.height
        wpercent = (basewidth / float(self.img.size[0]))
        hpercent = baseheight / float(self.img.size[1])
        hsize = int((float(self.img.size[1]) * float(wpercent)))

        if hsize > baseheight:
            hsize = baseheight

            basewidth = int((float(self.img.size[0]) * float(hpercent)))

        self.scaling_h = hpercent
        self.scaling_w = wpercent

        if self.last_image_size[0] == 0:
            self.last_image_size = [basewidth, hsize]

        scaled_image = self.img.resize((basewidth, hsize), Image.ANTIALIAS)
        self.images = [ImageTk.PhotoImage(scaled_image)]
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.images[0])
        self.update_points_scaling(basewidth, hsize)

    def update_points_scaling(self, new_width, new_height):
        """
        Moves the LEDs and anchor points of the image to be relatively at the same position on teh resized image
        with new_width and new_height
        :param new_width: The new width of the resized image
        :param new_height: The new height of the resized image
        """
        self.undone_points = list(map(lambda x: [int(x[0] * self.scaling_w), int(x[1] * self.scaling_h)], self.undone_points))
        self.undone_leds = list(map(lambda x: [int(x[0] * self.scaling_w), int(x[1] * self.scaling_h), x[2]], self.undone_leds))

        scaling_x = new_width / self.last_image_size[0]
        scaling_y = new_height / self.last_image_size[1]
        last_image_diagonal = pow(pow(self.last_image_size[0], 2) + pow(self.last_image_size[1], 2), 0.5)
        new_image_diagonal = pow(pow(new_width, 2) + pow(new_height, 2), 0.5)
        diagonal_scaling = new_image_diagonal / last_image_diagonal

        for i in range(len(self.leds)):
            led = self.leds.pop(0)
            self.canvas.delete(self.leds_references.pop(0))
            self.add_led_by_coordinates(round(led[0] * scaling_x), round(led[1] * scaling_y), round(led[2] * diagonal_scaling))

        for i in range(len(self.anchor_points)):
            anchor = self.anchor_points.pop(0)
            if self.current_state == CreationState.BOARD:
                self.canvas.delete(self.points.pop(0))
            self.add_point_by_coordinates(round(anchor[0] * scaling_x), round(anchor[1] * scaling_y))

        self.last_image_size = [new_width, new_height]

    def add_point_by_coordinates(self, x, y):
        """
        Creates a anchor point at the given coordinates.
        Only 4 anchor points can exist at the same time.
        :param x: The x coordinate of the anchor point.
        :param y: The y coordinates of the anchor point.
        """
        circles = self.check_hovered(x, y)
        if not circles:
            if len(self.anchor_points) >= 4:
                return

            if len(self.anchor_points) > 0:
                self.canvas.delete("poly")
            print(f"frame coordinates: {x}, {y}")
            self.anchor_points.append((x, y))
            anchor_point = self.create_circle(x, y, 10)
            self.points.append(anchor_point)
            self.update_polygon()
            self.active_circle = len(self.anchor_points) - 1
        else:
            self.active_circle = self.anchor_points.index(circles[0])

    def add_led_by_coordinates(self, x, y, radius=20):
        """
        Creates a LED at the given coordinates.
        :param radius: The radius of the led. Default value 20
        :param x: The x coordinates of the LED.
        :param y: The y coordinate of the LED.
        """
        circles = self.check_hovered(x, y)
        if not circles:
            led_ref = self.create_circle(x, y, radius)
            self.leds.append((x, y, radius))
            self.leds_references.append(led_ref)
            self.active_circle = len(self.leds) - 1
        else:
            self.active_circle = self.leds.index(circles[0])

    def redo_point(self):
        """
        Redo the last LED/point if available.
        """
        if self.current_state == CreationState.BOARD:
            if len(self.undone_points) > 0 and len(self.anchor_points) < 4:
                point = self.undone_points.pop()
                self.add_point_by_coordinates(point[0], point[1])
        if self.current_state == CreationState.LED:
            if len(self.undone_leds) > 0:
                led = self.undone_leds.pop()
                self.add_led_by_coordinates(led[0], led[1])

    def undo_point(self):
        """
        Undo the last set LED or Anchor point.
        The undone led/point is saved in a list for the redo operation.
        """
        if self.current_state == CreationState.BOARD:
            if len(self.anchor_points) > 0:
                coordinates_point = self.anchor_points.pop()
                point = self.points.pop()
                self.undone_points.append(coordinates_point)
                self.canvas.delete(point)
                self.update_polygon()
        if self.current_state == CreationState.LED:
            if len(self.leds) > 0:
                led = self.leds.pop()
                self.undone_leds.append(led)
                ref = self.leds_references.pop()
                self.canvas.delete(ref)



    def check_hovered(self, cx, cy):
        """
        Helper function for checking the currently hovered anchor point or LED.
        :param cx: The x coordinate to check
        :param cy: The y coordinate to check
        :return:
        """
        circles = filter(lambda x: distance.euclidean((cx, cy), x) <= 10, self.anchor_points)
        if self.current_state == CreationState.BOARD:
            circles = filter(lambda x: distance.euclidean((cx, cy), x) <= 10, self.anchor_points)
        if self.current_state == CreationState.LED:
            circles = filter(lambda x: distance.euclidean((cx, cy), (x[0], x[1])) <= x[2], self.leds)
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
        """
        Moves the currently selected anchor point or LED
        :param event:
        """
        print(f"hover circle: {event.x} {event.y}")
        print(f"active circle: {self.active_circle}")

        if self.current_state == CreationState.BOARD:
            anchor_point_ref = self.points[self.active_circle]
            self.anchor_points[self.active_circle] = (event.x, event.y)
            self.canvas.coords(anchor_point_ref, event.x - 10, event.y - 10, event.x + 10, event.y + 10)
            self.update_polygon()
        if self.current_state == CreationState.LED:
            led_ref = self.leds_references[self.active_circle]
            radius = self.leds[self.active_circle][2]
            self.leds[self.active_circle] = (event.x, event.y, radius)
            self.canvas.coords(led_ref, event.x - radius, event.y - radius, event.x + radius, event.y + radius)


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
            self.canvas.bind("<Button-1>", lambda e: self.add_point_by_coordinates(e.x, e.y))
            self.canvas.bind("<Button-3>", self.remove_anchor_point)
            self.canvas.bind("<B1-Motion>", self.moving_anchor)
            self.canvas.unbind("<MouseWheel>")  # On Windows
            self.canvas.unbind("<Button-4>")  # On Linux
            self.canvas.unbind("<Button-5>")  # On Linux
            self.draw_circles()
        if self.current_state == CreationState.LED:
            self.delete_circles()
            self.canvas.bind("<Button-1>", lambda e: self.add_led_by_coordinates(e.x, e.y))
            self.canvas.bind("<MouseWheel>", self.on_mousewheel)  # On Windows
            self.canvas.bind("<Button-4>", self.on_mousewheel)  # On Linux
            self.canvas.bind("<Button-5>", self.on_mousewheel)  # On Linux



    def on_mousewheel(self, event):
        """
        Changes the size of the currently hovered LED.
        :param event:
        """
        count = 0
        if event.num == 5 or event.delta == -120:
            count = -1
        if event.num == 4 or event.delta == 120:
            count = 1

        circles = self.check_hovered(event.x, event.y)
        if circles:
            
            active_led = circles[0]
            index = self.leds.index(active_led)
            led_ref = self.leds_references[index]

            radius = active_led[2] + count
            self.leds[index] = (active_led[0], active_led[1], radius)
            self.canvas.coords(led_ref, active_led[0] - radius, active_led[1] - radius, active_led[0] + radius, active_led[1] + radius)
        


    def remove_anchor_point(self, event):
        """
        removes an anchor_point
        :param event: is a Mouse event
        :return:
        """
        circles = self.check_hovered(event.x, event.y)
        if circles[0] is not None:
            if self.current_state == CreationState.BOARD:
                index = self.anchor_points.index(circles[0])

                point = self.points[index]

                self.canvas.delete(point)
                self.anchor_points.remove(circles[0])
                self.points.remove(point)
                self.update_polygon()
            
            if self.current_state == CreationState.LED:
                index = self.leds.index(circles[0])
                ref = self.leds_references[index]
                self.canvas.delete(ref)
                self.leds.remove(circles[0])
                self.leds_references.remove(ref)


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








