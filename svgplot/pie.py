import math
from collections.abc import Iterable

import numpy as np

from . import svgfiguredraw
from .svgfigure import SVGFigure


def add_pie_chart(svg: SVGFigure,
                  values: Iterable[float],
                  colors: Iterable[str] = None,
                  labels: Iterable[str] = None,
                  labelcolors: str = 'white',
                  labelradius: float = 0.5,
                  edgecolor: str = 'black',
                  pos: tuple[float, float] = (0, 0),
                  r: int = 150,
                  labelrmap: dict[str, any] = {},
                  stroke: int = 2):
    x, y = pos

    if colors is None:
        colors = ['blue']

    if labels is not None:
        labels = np.array(labels)

    if isinstance(labelcolors, str):
        labelcolors = [labelcolors]

    labelcolors = np.array(labelcolors)

    colors = np.array(colors)

    fracs = np.array(values)
    fracs = fracs / fracs.sum()

    angle1 = 0
    angle2 = 0
    labelradius = r * labelradius

    for i in range(0, fracs.size):
        f = fracs[i]
        angle2 = round(360 * f)

        # svgplot.rgbtohex(colors[i % colors.size])
        col = colors[i % colors.size]

        svg.add_arc(x=x, y=y, w=r*2, h=r*2, angle1=angle1,
                    angle2=angle2, fill=col, color=edgecolor, stroke=stroke)

        angle3 = (angle1 + angle2) / 2
        angle3 = angle3 / 360 * svgfiguredraw.TWO_PI_RADS

        angle1 += angle2

        # break

    if labels is not None:
        angle1 = 0
        angle2 = 0

        for i in range(0, fracs.size):
            f = fracs[i]
            angle2 = round(360 * f)

            angle3 = angle1 + angle2 / 2

            angle4 = angle3 / 360 * svgfiguredraw.TWO_PI_RADS

            lr = labelradius

            if i in labelrmap:
                lr *= labelrmap[i]

            if angle3 > 270:
                x1 = x + lr * math.sin(angle4)
                y1 = y - lr * math.cos(angle4)
            elif angle3 > 180:
                x1 = x + lr * math.sin(angle4)
                y1 = y - lr * math.cos(angle4)
            elif angle3 > 90:
                x1 = x + lr * math.sin(angle4)
                y1 = y - lr * math.cos(angle4)
            else:
                x1 = x + lr * math.sin(angle4)
                y1 = y - lr * math.cos(angle4)

            svg.add_text_bb(labels[i % labels.size], x=x1, y=y1,
                            align='c', color=labelcolors[i % labelcolors.size])

            angle1 += angle2
