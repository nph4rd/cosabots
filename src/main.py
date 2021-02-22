"""
Handler code for the lambda
"""

import json
import random

import numpy as np
import requests
from PIL import Image
from scipy.ndimage.filters import gaussian_filter
from scipy.ndimage.interpolation import map_coordinates

from keys import TELE_TOKEN

URL = f"https://api.telegram.org/bot{TELE_TOKEN}/"
FILE_URL = f"https://api.telegram.org/file/bot{TELE_TOKEN}/"


def send_message(text, chat_id):
    """
    Send a message with {text} to chat with {chat_id}
    """
    final_text = "You said: " + text
    url = URL + f"sendMessage?text={final_text}&chat_id={chat_id}"
    requests.get(url)


def lambda_handler(event, context):
    """
    Handle basic bot functionality
    """
    message = json.loads(event["body"])
    chat_id = message["message"]["chat"]["id"]
    try:
        file_id = message["message"]["photo"][-1]["file_id"]
    except KeyError as err:
        print(f"There was no photo. Error: {err}")
    print(message["message"])
    image_data = requests.get(URL + f"getFile?file_id={file_id}")
    image_data = json.loads(image_data.content)
    file_path = image_data["result"]["file_path"]
    image = requests.get(FILE_URL + file_path)
    file = open("/tmp/image.png", "wb")
    file.write(image.content)
    file.close()
    # Read image:
    img = np.asarray(Image.open("/tmp/image.png"))
    elastic_transform(img, "/tmp/transformed_image.png")
    files = {"photo": open("/tmp/transformed_image.png", "rb")}
    requests.post(URL + "sendPhoto?chat_id={}".format(chat_id), files=files)
    return {"statusCode": 200}


def elastic_transform(
    img,
    directory,
    alpha=random.randint(900, 1000),
    sigma=random.randint(4, 8),
    random_state=None,
):
    """Elastic deformation of imgs as described in [Simard2003]_.
    .. [Simard2003] Simard, Steinkraus and Platt, "Best Practices for
       Convolutional Neural Networks applied to Visual Document Analysis", in
       Proc. of the International Conference on Document Analysis and
       Recognition, 2003.
    """
    if random_state is None:
        random_state = np.random.RandomState(None)

    shape = img.shape
    dx = (
        gaussian_filter(
            (random_state.rand(*shape) * 2 - 1), sigma, mode="constant", cval=0
        )
        * alpha
    )
    dy = (
        gaussian_filter(
            (random_state.rand(*shape) * 2 - 1), sigma, mode="constant", cval=0
        )
        * alpha
    )
    dz = np.zeros_like(dx)

    x, y, z = np.meshgrid(np.arange(shape[1]), np.arange(shape[0]), np.arange(shape[2]))
    print(x.shape)
    indices = (
        np.reshape(y + dy, (-1, 1)),
        np.reshape(x + dx, (-1, 1)),
        np.reshape(z, (-1, 1)),
    )

    distored_img = map_coordinates(img, indices, order=1, mode="reflect")
    dist_reshaped = distored_img.reshape(img.shape)
    dist_reshaped = Image.fromarray(dist_reshaped)
    dist_reshaped.save(directory)


__import__("pdb").set_trace()
