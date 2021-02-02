# -*- coding: utf-8 -*-

"""
======
FILTER
======

Console script.
"""

from __future__ import absolute_import, division, print_function

from glob import glob
from random import randrange
from typing import List, Tuple, Union

from blend_modes import difference
import numpy as np
from PIL import Image as pil
from PIL import ImageFilter as fil
from PIL.Image import Image

#####################################################################
# SCALE
#####################################################################

def scale_wrapping_image(
        w1: int,
        h1: int,
        ratio: float=1.5) -> Tuple[int, int]:
    """
    Scale an image so that it wraps around the input image size.
    Also square the wrapper image.

    Parameters
    ----------

    Returns
    -------
    out: None.
    """
    return (
        int(max(1., ratio) * max(w1, h1)),
        int(max(1., ratio) * max(w1, h1)))

#####################################################################
# POSITION
#####################################################################

def position_inside(
        w1: int,
        h1: int,
        w2: int,
        h2: int) -> Union[None, Tuple[int, int]]:
    """
    Position an image randomly, while remaining entirely inside a
    container image.

    Parameters
    ----------

    Returns
    -------
    out: None.
    """
    if (w2 >= w1) and (h2 >= h1):
        return (
            randrange(0, 1 + w2 - w1),  # 0 if w2 == w1
            randrange(0, 1 + h2 - h1))  # same
    else:
        return None

def move_around(
        x: int,
        y: int,
        w1: int,
        h1: int,
        w2: int,
        h2: int,
        limit: int=10) -> Union[None, Tuple[int, int]]:
    """
    Slightly move the smaller image around its position, inside
    the larger image.

    Actually the composition of 4 unidirectional movements, in
    each margin space before and after the smaller image.

    Parameters
    ----------

    Returns
    -------
    out: None.
    """
    if (w2 >= x + w1) and (h2 >= y + h1):
        x_before = randrange(0, 1 + min(limit, x))
        x_after = randrange(0, 1 + min(limit, w2 - w1 - x))
        y_before = randrange(0, 1 + min(limit, y))
        y_after = randrange(0, 1 + min(limit, h2 - h1 - y))
        return (
            x_after - x_before,
            y_after - y_before)
    else:
        return None

#####################################################################
# NOISE
#####################################################################

# so far, randomly move_arounding the texture does the job
# could be combined with random flip & rotation

#####################################################################
# LAYERS BLENDING
#####################################################################

# so far, blend_modes does the job

#####################################################################
# INPUT
#####################################################################

#####################################################################
# OUTPUT
#####################################################################

def merge_into_an_animation(
        images: List[Image],
        path: str="./out.gif") -> None:
    """
    Merge a list of images into a gif.

    Parameters
    ----------
    images: List.
        A list of image objects, one for each frame.
    path: str.
        The location of the output gif.

    Returns
    -------
    out: None.
    """
    __first, __rest = images[:1], images[1:]
    if __first and __rest:
        __first[0].save(
            fp=path,
            format='GIF',
            append_images=__rest,
            save_all=True,
            duration=100,
            loop=0,
            optimize=True)

#####################################################################
# FULL TRANSITION
#####################################################################

def apply_scan_filter(
        image: Image,
        texture: Image,
        position: Tuple[int, int],
        limit: int=10,
        opacity: int=0.7) -> Image:
    __x, __y = position
    __wi, __hi = image.size
    __wt, __ht = texture.size

    # add a random move_around as noise
    # to simulate the imperfect alignment of a picture in a scanner
    __dx, __dy = move_around(
        x=__x,
        y=__y,
        w1=__wi,
        h1=__hi,
        w2=__wt,
        h2=__ht,
        limit=limit) # don't move more than 10 pixels along each axis

    # crop the texture to match the input image size
    __mask = texture.crop((
        __x + __dx,
        __y + __dy,
        __x + __dx + __wi,
        __y + __dy + __hi))

    # blend the mask and the input image
    __filtered = pil.fromarray(np.uint8(difference(
        np.array(image).astype(float),
        np.array(__mask).astype(float),
        opacity=opacity)))

    # sharpen the result
    return __filtered.filter(fil.SHARPEN)

#####################################################################
# MAIN
#####################################################################

if __name__ == "__main__":
    with pil.open('/home/flatline/images/projects/2021-01_eat-away-filter/input/back.png').convert('LA').convert('RGBA') as __input:
        with pil.open('/home/flatline/images/projects/2021-01_eat-away-filter/textures/squared/3.png').convert('LA').convert('RGBA') as __texture:

            # globals
            __input.thumbnail((768, 768), reducing_gap=3.0)
            __wi, __hi = __input.size
            __frames = [__input]

            # resize the texture to 1.5 x input, so that it wraps the input
            __texture = __texture.resize(scale_wrapping_image(
                __wi,
                __hi,
                1.5))
            __wt, __ht = __texture.size

            # initiate
            __current = __input
            
            # position the image inside the texture
            __position = position_inside(
                w1=__wi,
                h1=__hi,
                w2=__wt,
                h2=__ht)

            for i in range(30):
                # filter the current iteration
                __current = apply_scan_filter(
                    image=__current,
                    texture=__texture,
                    position=__position,
                    limit=8,
                    opacity=0.8)

                # save the current frame
                __frames.append(__current)

    merge_into_an_animation(__frames, '/home/flatline/test.gif')
