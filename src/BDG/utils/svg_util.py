import lxml
from lxml import etree
from PIL import Image
import pathlib
import base64


def convert_image_to_data_uri(path: str):
    '''
    reads an image from path and converts it to a data uri scheme as string

    :param path:
    :return:
    '''

    type = pathlib.Path(path).suffix[1:]  # removing dot

    prefix = f"data:image/{type};base64,"

    with open(path, 'rb') as binary_file:
        binary_file_data = binary_file.read()
        base64_encoded_data = base64.b64encode(binary_file_data)
        base64_message = base64_encoded_data.decode('utf-8')
        datauri = prefix + base64_message
        return datauri


class SVGCreator():
    def __init__(self, path):

        file_type = pathlib.Path(path).suffix[1:]
        if file_type == 'svg':
            tree = etree.parse(path)
            self.root = tree.getroot()
        else:
            self.root = etree.Element("svg",
                                      nsmap={None: 'http://www.w3.org/2000/svg'},
                                      xmlns="http://www.w3.org/2000/svg")
            self.insert_image(path)

    def insert_image(self, img_path):
        '''
        insert or replaces the board image
        :param img_path: is a path to a rasterized image ('png','jpg','gif')
        :return:
        '''
        im = Image.open(img_path)
        width, height = im.size
        self.root.set("width", str(width))
        self.root.set("height", str(height))

        img = self.root.find("image")
        if img is None:
            img = etree.Element("image")
            self.root.append(img)

        img.set("width", str(width))
        img.set("height", str(height))
        img.set("href", convert_image_to_data_uri(img_path))

    def add_led(self, x, y, w, h, led_id):
        '''
        adds a led description on the given coordinates
        which is represented as rectangle with attribute "component_type" = "led"
        :param x: is the x coordinate
        :param y: is the y coordinate
        :param led_id: is an unique identifier
        :return:
        '''

        etree.SubElement(self.root, "rect",
                         x=str(x), y=str(y),
                         width=str(w), height=str(h),
                         id=str(led_id),
                         component_type="led")

    def get_led(self, led_id):
        '''
        returns the led_id element by the given led_id
        :param led_id:
        :return:
        '''
        led = self.root.xpath(f"/rect[@component_type='led'][@id={led_id}]")
        assert(len(led) != 0)
        return led[0]

    def resize_led(self, led_element:etree.SubElement, delta_w, delta_h):
        '''
        resizing led
        :param led_element:
        :param delta_w:
        :param delta_h:
        :return:
        '''
        width = float(led_element.get('width'))
        height = float(led_element.get('height'))
        width += delta_w
        height += delta_h

        led_element.set('width', str(width))
        led_element.set('height', str(height))

    def move_led(self, led_element:etree.SubElement, delta_x, delta_y):
        x = float(led_element.get('width'))
        y = float(led_element.get('height'))
        x += delta_x
        y += delta_y

        led_element.set('x', str(x))
        led_element.set('y', str(y))









    def write_to_file(self, filename):
        '''
        writes to a file

        :param filename: is a name for a file
        :return:
        '''
        f = open(filename + "svg", "wb")

        f.write(
            etree.tostring(
                etree.ElementTree(self.root),
                xml_declaration=True,
                standalone=False,
                encoding="UTF-8",
                pretty_print=True
            )
        )
        f.close()
