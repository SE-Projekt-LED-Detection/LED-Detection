import tkinter as tk
from enum import Enum

from PIL import Image, ImageDraw, ImageTk

from scipy.spatial import distance


class CreationState(Enum):
    BOARD = "board"
    LED = "led"


class ImagePane(tk.Frame):
    def __init__(self, container):
        tk.Frame.__init__(self, container)
        self.master = container
        self.images = None
        self.img_path = None
        self.polygon = None
        self.polygon_images = {}
        self.canvas = tk.Canvas(container, height=400, width=400)
        self.canvas.pack()
        self.points = []
        self.anchor_points = []
        self.active_circle = 0
        self.change_state(CreationState.BOARD)
        self.but = tk.Button(container, text="Toggle ", command=self.toggle_state)
        self.but.pack()

    def choose_image(self, img_path):
        self.img_path = img_path
        img = Image.open(self.img_path)
        self.images = [ImageTk.PhotoImage(img)]
        w = self.images[0].width()
        h = self.images[0].height()
        self.canvas.config(width=w, height=h)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.images[0])
        self.canvas.pack()

    def add_point(self, event):
        circles = self.check_hovered(event.x, event.y)
        if not circles:
            if len(self.points) > 0:
                self.canvas.delete("poly")
            print(f"frame coordinates: {event.x}, {event.y}")
            self.points.append((event.x, event.y))
            anchor_point = self.create_circle(event.x, event.y, 10)
            self.anchor_points.append(anchor_point)
            self.update_polygon()
            self.active_circle = len(self.points) - 1
        else:
            self.active_circle = self.points.index(circles[0])

    def undo_point(self):
        self.points.pop()
        point = self.anchor_points.pop()
        self.canvas.delete(point)
        self.update_polygon()

    def check_hovered(self, cx, cy):
        circles = filter(lambda x: distance.euclidean((cx, cy), x) <= 10, self.points)
        return list(circles)

    def create_circle(self, x, y, r):
        x0 = x - r
        y0 = y - r
        x1 = x + r
        y1 = y + r
        return self.canvas.create_oval(x0, y0, x1, y1)

    def draw_circles(self):
        for point in self.points:
            anchor_point = self.create_circle(point[0], point[1], 10)
            self.anchor_points.append(anchor_point)

    def delete_circles(self):
        for ref in self.anchor_points:
            self.canvas.delete(ref)
        self.anchor_points = []

    def moving_anchor(self, event):
        print(f"hover cirle: {event.x} {event.y}")
        print(f"active cirle: {self.active_circle}")
        anchor_point_ref = self.anchor_points[self.active_circle]
        self.points[self.active_circle] = (event.x, event.y)
        self.canvas.coords(anchor_point_ref, event.x - 10, event.y - 10, event.x + 10, event.y + 10)
        self.update_polygon()

    def update_polygon(self):
        if self.polygon is not None:
            self.canvas.delete(self.polygon)
        if len(self.points) > 1:
            points = [y for x in self.points for y in x]
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
        self.current_state = state
        if self.current_state == CreationState.BOARD:
            self.canvas.bind("<Button-1>", self.add_point)
            self.canvas.bind("<B1-Motion>", self.moving_anchor)
            self.draw_circles()
        if self.current_state == CreationState.LED:
            self.delete_circles()
            self.canvas.bind("<Button-1>", self.add_led)#
            self.canvas.unbind("<B1-Motion>")


    def toggle_state(self):
        if self.current_state == CreationState.BOARD:
            self.change_state(CreationState.LED)
        else:
            self.change_state(CreationState.BOARD)

    def add_led(self, event):
        self.create_circle(event.x, event.y, 20)
