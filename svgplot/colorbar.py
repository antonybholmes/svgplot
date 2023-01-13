from typing import Optional
from .axis import Axis
from .svgfigure import SVGFigure
from . import core
from . import graph
import numpy as np
import matplotlib


def add_h_colorbar(svg: SVGFigure,
                   pos: tuple[int, int] = (0, 0),
                   dim: tuple[int, int] = (300, 25),
                   steps=15,
                   cmap=matplotlib.cm.viridis,
                   ticks=None,
                   ticklabels: Optional[list[str]] = None,
                   axis=None,
                   norm: matplotlib.colors.Normalize = None,
                   showframe: bool = True,
                   showaxis: bool = True,
                   stroke: int = 2,
                   align: str = 'c'):
    x, y = pos
    w, h = dim

    if align == 'c':
        x -= w/2

    if axis is None:
        axis = Axis(lim=[0., 1.], w=w)
    elif isinstance(axis, list) or isinstance(axis, tuple):
        axis = Axis(lim=[axis[0], axis[1]], w=w)
    else:
        pass

    if norm is None:
        norm = matplotlib.colors.Normalize(
            vmin=axis.lim[0], vmax=axis.lim[1])

    if ticks is None:
        mid = (axis.lim[0] + axis.lim[1]) / 2

        if mid == 0:
            mid = 0

        ticks = [axis.lim[0], mid, axis.lim[1]]

    if ticklabels is None:
        ticklabels = ticks

    if steps is None:
        steps = int(cmap.N / 2)

    # define where each color block starts
    # if we have 3 steps they begin at 0,1,2
    # so we normalized by dividing by the number
    # of steps (one more than the index of the)
    # last step since the last step begins before
    # the end of the rect.If there are
    # 3 steps/blocks then the distance between blocks is 1/3
    # and the offset is 1/3 * 1/2 since the first point is
    # midway through the first block whose width is 1/3.
    steps_color_x = np.array(range(0, steps))
    steps_color_x = steps_color_x / steps_color_x.size + (0.5 / steps_color_x.size)

    # distance to start of next block i.e. step/block width
    x_inc = w / steps_color_x.size
    
    max_color_index = cmap.N - 1

    x_off = 0

    #w1 = x_inc * 2
    
    for stepi, step_color_x in enumerate(steps_color_x):
        #xoff = xaxis.scale(step_x)
        w1 = w - x_off
        col = core.rgbtohex(cmap(int(step_color_x * max_color_index)))
        print(stepi, step_color_x, step_color_x, int(step_color_x * max_color_index), col)
        svg.add_rect(x=x+x_off, y=y, w=w1, h=h, fill=col)
        x_off += x_inc

    if showaxis:
        graph.add_x_axis(svg,
                         pos=(x, y+h+5),
                         axis=axis,
                         ticks=ticks,
                         ticklabels=ticklabels,
                         showticks=True,
                         showline=False)

    if showframe:
        svg.add_frame(x, y=y, w=w, h=h, stroke=stroke)


def add_v_colorbar(svg,
                   pos: tuple[int, int] = (0, 0),
                   dim: tuple[int, int] = (25, 200),
                   steps=15,
                   cmap=matplotlib.cm.viridis,
                   ticks=None,
                   ticklabels=None,
                   axis=None,
                   norm=None,
                   showframe=True,
                   showaxis=True,
                   stroke=2,
                   align='c'):
    x, y = pos
    w, h = dim

    if axis is None:
        axis = Axis(lim=[0., 1.], w=h)
    elif isinstance(axis, list) or isinstance(axis, tuple):
        axis = Axis(lim=[axis[0], axis[1]], w=h)
    else:
        pass

    if norm is None:
        norm = matplotlib.colors.Normalize(
            vmin=axis.lim[0], vmax=axis.lim[1])

    if ticks is None:
        mid = (axis.lim[0] + axis.lim[1]) / 2

        if mid == 0:
            mid = 0

        ticks = [axis.lim[0], mid, axis.lim[1]]

    if ticklabels is None:
        ticklabels = ticks

    if steps is None:
        steps = int(cmap.N / 2)

    steps_color_y = np.array(range(0, steps))
    steps_color_y = steps_color_y / steps_color_y.size + (0.5 / steps_color_y.size)

    # distance to start of next block i.e. step/block width
    y_inc = h / steps_color_y.size

    max_color_index = cmap.N - 1

    y_off = h
    
    for stepi, step_color_y in enumerate(steps_color_y):
        col = core.rgbtohex(cmap(int(step_color_y * max_color_index)))
        print(stepi, step_color_y, step_color_y, int(step_color_y * max_color_index), col)
        svg.add_rect(x=x, y=y, w=w, h=y_off, fill=col)
        y_off -= y_inc

    if showaxis:
        graph.add_y_axis(svg, 
                         pos=(x+w+5, y),
                         axis=axis,
                         ticks=ticks,
                         ticklabels=ticklabels,
                         showticks=True,
                         showline=False,
                         side='r')

    if showframe:
        svg.add_frame(x, y=y, w=w, h=h, stroke=stroke)
