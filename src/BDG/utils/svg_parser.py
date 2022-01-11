from lxml import etree
import matplotlib.pyplot as plt
from dataclasses import dataclass
import base64
import numpy as np
import cv2
import typing


@dataclass
class LED_ROI:
    x: int
    y: int
    width: int
    height: int
    id: str = "123456"
    description: str = "just some random description"


def load_svg(path: str):
    """
    loads an svg file and returns the root

    Args:
        path (str): path to the svg file

    Returns:
        [type]: [description]
    """
    tree = etree.parse(path)
    return tree.getroot()


def get_all_rect(root, attribute="led"):
    rects = root.xpath('//svg:rect', namespaces={   'svg': "http://www.w3.org/2000/svg"  })

    rect_obj = []

    for rect in rects:
        x = (float(rect.get('x')))
        y = (float(rect.get('y')))
        width = (float(rect.get('width')))
        height = (float(rect.get('height')))
        id = rect.get('id')
        description = rect.get('description')
        rect_obj.append(LED_ROI(x, y, width, height, id, description))
    return rect_obj


def decode_img_data(img_attr: str):
    """Decodes the embedded image string.

    Args:
        img_attr (str): is the href data
    """

    mime_to_extension = {
        'image/gif': '.gif',
        'image/jpeg': '.jpg',
        'image/png': '.png',
    }
    media_data, data = img_attr.split(',', 1)
    jpg_original = base64.b64decode(data)
    jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
    img = cv2.imdecode(jpg_as_np, flags=cv2.IMREAD_COLOR)
    plt.imshow(img)
    plt.show
    return img


def parse_embedded_image(svg):
    """
    parses in svg embedded jpg image and returns it as np.array
    :param svg: is an lxml tree
    :return: BGR-image as np.array
    """
    image = svg.xpath('//svg:image', namespaces={'svg': "http://www.w3.org/2000/svg"})[0]
    data = image.attrib['{http://www.w3.org/1999/xlink}href']
    return decode_img_data(data)

def extract_roi(rois:typing.List[LED_ROI],img):
    croped_img_lst = []
    for roi in rois:
        cropped_img = img[roi.y:roi.y + roi.height, roi.x:roi.x + roi.width]
        plt.imshow(cropped_img)
        plt.title(roi.id)
        plt.show()
        croped_img_lst.append(cropped_img)
    return croped_img_lst





