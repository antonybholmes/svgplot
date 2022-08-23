from typing import Mapping, Optional, Union, Any
from .axis import Axis
from .svgfigure import SVGFigure
from . import svgfiguredraw
import numpy as np
import math
from . import graph
from enum import Enum
import pandas

import random
import string

LETTERS = string.ascii_lowercase


def get_rand_id(l=10):
    return ''.join(random.choice(LETTERS) for i in range(l))


def add_hatch(svg: SVGFigure,
              x: int = 0,
              y: int = 0,
              w: int = 0,
              h: int = 0,
              hatch='solid',
              color='gray',
              dh=[50, 20],
              id: str = '',
              frame=False):

    y1 = y
    y2 = y + h
    x1 = x
    x2 = x + w

    if id == '':
        id = get_rand_id()

    print(id)

    match hatch:
        case 'x':
            clip_path = svg.svg.defs.add(svg.svg.clipPath(id=id))
            # things inside this shape will be drawn
            clip_path.add(svg.svg.rect(
                insert=(svg.x(x1), svg.y(y1)), size=(w, h)))

            yh1 = y2 + dh[0]
            yh2 = yh1 - dh[0]

            while yh1 > y1:
                svg.add_line(x1=x1, x2=x2, y1=yh1, y2=yh2,
                             color=color, clip_path=f"url(#{id})")
                yh1 -= dh[1]
                yh2 -= dh[1]

            yh1 = y2
            yh2 = yh1 + dh[0]

            while yh2 > y1:
                svg.add_line(x1=x1, x2=x2, y1=yh1, y2=yh2,
                             color=color, clip_path=f"url(#{id})")
                yh1 -= dh[1]
                yh2 -= dh[1]
        case '/':
            clip_path = svg.svg.defs.add(svg.svg.clipPath(id=id))
            # things inside this shape will be drawn
            clip_path.add(svg.svg.rect(
                insert=(svg.x(x1), svg.y(y1)), size=(w, h)))

            yh1 = y2 + dh[0]
            yh2 = yh1 - dh[0]

            while yh1 > y1:
                svg.add_line(x1=x1, x2=x2, y1=yh1, y2=yh2,
                             color=color, clip_path=f"url(#{id})")
                yh1 -= dh[1]
                yh2 -= dh[1]

        case _:
            svg.add_rect(x1, y1, w, h, fill=color)

    if frame: 
      svg.add_rect(x1, y1, w, h, color='black')