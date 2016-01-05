"""
This is a test script for playing with images. I'm actually copying most of this file (that's the plan anyway) from
a script reddit hosts on github. It's how they turn images to str, str to image and crop images with python. So I'm
not going to clone their script, just pick and choose a few parts to see if I can integrate it into this project. If
not then I'll probably scrap this file and just do basic str to image, image to str with StringIO
"""

import cStringIO, StringIO


def _image_to_str(image):
    str = cStringIO.StringIO()
    image.save(str, image.format)
    return str.getvalue()

