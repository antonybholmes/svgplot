import math
from collections.abc import Iterable
import re
from typing import Union

import numpy as np

from . import svgfiguredraw
from .svgfigure import SVGFigure


def add_pie_chart(
    svg: SVGFigure,
    values: Iterable[float],
    colors: Iterable[str] = None,
    innerlabels: Union[str, Iterable[str]] = "%",
    innerlabelcolors: str = "white",
    innerlabelradius: float = 0.5,
    outerlabels: Union[str, Iterable[str]] = None,
    outerlabelcolors: str = "black",
    outerlabelradius: float = 1.15,
    edgecolor: str = "black",
    pos: tuple[float, float] = (0, 0),
    r: int = 200,
    labelrmap: dict[str, any] = {},
    stroke: int = 2,
    start_angle: int = 0,
    explode: int = 0,
):
    x, y = pos

    if colors is None:
        colors = ["blue"]

    if isinstance(innerlabels, str):
        innerlabels = [innerlabels]

    if innerlabels is not None:
        innerlabels = np.array(innerlabels)

    if isinstance(innerlabelcolors, str):
        innerlabelcolors = [innerlabelcolors]

    innerlabelcolors = np.array(innerlabelcolors)

    if isinstance(outerlabels, str):
        outerlabels = [outerlabels]

    if outerlabels is not None:
        outerlabels = np.array(outerlabels)

    if isinstance(outerlabelcolors, str):
        outerlabelcolors = [outerlabelcolors]

    outerlabelcolors = np.array(outerlabelcolors)

    colors = np.array(colors)

    fracs = np.array(values)
    fracs = fracs / fracs.sum()

    angle1 = 0
    degs = 0

    for i in range(0, fracs.size):
        f = fracs[i]
        degs = round(360 * f)
        angle2 = angle1 + degs

        # svgplot.rgbtohex(colors[i % colors.size])
        col = colors[i % colors.size]

        angle3 = start_angle + (angle1 + angle2) / 2
        rad_angle = angle3 / 360 * svgfiguredraw.TWO_PI_RADS

        xr = explode * math.sin(rad_angle)

        # if angle3 > 180 and angle3 < 270:
        #    xr = -xr

        print(angle1, degs, angle3, xr)

        x1 = x + xr
        y1 = y - explode * math.cos(rad_angle)

        svg.add_arc(
            x=x1,
            y=y1,
            w=r * 2,
            h=r * 2,
            angle1=start_angle + angle1,
            angle2=start_angle + degs,
            fill=col,
            stroke=0,
        )

        angle1 = angle2

    # stroke lines

    if stroke > 0:
        angle1 = 0
        degs = 0

        for i in range(0, fracs.size):
            f = fracs[i]
            degs = round(360 * f)
            angle2 = angle1 + degs

            # stroke lines

            rad_angle = angle1 / 360 * svgfiguredraw.TWO_PI_RADS
            x1 = x + r * math.sin(rad_angle)
            y1 = y - r * math.cos(rad_angle)
            svg.add_line(x1=x, y1=y, x2=x1, y2=y1, color=edgecolor, stroke=stroke)

            angle1 = angle2

        # smooth the center point where the separator lines meet
        svg.add_circle(x, y, stroke, fill=edgecolor)

        # put a border around the end of the pie
        svg.add_circle(x, y, r * 2, color=edgecolor)

    #
    # Inner labels
    #

    if innerlabels is not None:
        fs = svg._font_size
        svg.set_font_size(8)

        if innerlabels[0].startswith("%"):
            # plot percentages
            dp = 0

            matcher = re.search(r":(\d)", innerlabels[0])

            if matcher:
                dp = int(matcher.group(1))

            print("df", dp, f"{{0:{dp}f}}")

            innerlabels = np.array([f"{{:.{dp}f}}%".format(x * 100) for x in fracs])

        innerlabelradius = r * innerlabelradius
        angle1 = 0
        degs = 0

        for i in range(0, fracs.size):
            f = fracs[i]
            degs = round(360 * f)

            angle3 = start_angle + angle1 + degs / 2

            rad_angle = angle3 / 360 * svgfiguredraw.TWO_PI_RADS

            lr = innerlabelradius

            if i in labelrmap:
                lr *= labelrmap[i]

            x1 = x + lr * math.sin(rad_angle)
            y1 = y - lr * math.cos(rad_angle)

            label = innerlabels[i % innerlabels.size]

            if isinstance(label, str):
                label = [label]

            y2 = y1
            for l in label:
                svg.add_text_bb(
                    l,
                    x=x1,
                    y=y2,
                    align="c",
                    color=innerlabelcolors[i % innerlabelcolors.size],
                )
                y2 += 40

            angle1 += degs

        svg.set_font_size(fs)

    #
    # Outer labels
    #
    if outerlabels is not None:
        outerlabelradius = r * outerlabelradius
        angle1 = 0
        degs = 0

        for i in range(0, fracs.size):
            f = fracs[i]
            degs = round(360 * f)

            angle3 = start_angle + angle1 + degs / 2

            rad_angle = angle3 / 360 * svgfiguredraw.TWO_PI_RADS

            lr = outerlabelradius

            if i in labelrmap:
                lr *= labelrmap[i]

            x1 = x + lr * math.sin(rad_angle)
            y1 = y - lr * math.cos(rad_angle)

            label = outerlabels[i % outerlabels.size]

            if isinstance(label, str):
                label = [label]

            print(
                label, outerlabelcolors[i % outerlabelcolors.size], x1, y1, lr, angle3
            )

            if angle3 > 300:
                align = "c"
            if angle3 > 190:
                align = "r"
            elif angle3 > 179:
                align = "c"
            else:
                align = "l"

            y2 = y1
            for l in label:
                svg.add_text_bb(
                    l,
                    x=x1,
                    y=y2,
                    align=align,
                    color=outerlabelcolors[i % outerlabelcolors.size],
                )
                y2 += 40

            angle1 += degs
