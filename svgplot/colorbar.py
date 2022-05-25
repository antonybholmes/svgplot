from .axis import Axis
from .svgfigure import SVGFigure
from . import svgplot
from . import graph
import numpy as np
import matplotlib


def add_colorbar(svg: SVGFigure,
                 x=0,
                 y=0,
                 w=300,
                 h=32,
                 steps=None,
                 cmap=matplotlib.cm.viridis,
                 ticks=None,
                 ticklabels=None,
                 xaxis=None,
                 norm=None,
                 showframe=True,
                 showaxis=True,
                 stroke=2,
                 align='c'):
    if align == 'c':
        x -= w/2

    if xaxis is None:
        xaxis = Axis(lim=[0., 1.], w=w)
    elif isinstance(xaxis, list) or isinstance(xaxis, tuple):
        xaxis = Axis(lim=[xaxis[0], xaxis[1]], w=w)
    else:
        pass

    if norm is None:
        norm = matplotlib.colors.Normalize(
            vmin=xaxis.lim[0], vmax=xaxis.lim[1])

    if ticks is None:
        mid = (xaxis.lim[0] + xaxis.lim[1]) / 2

        if mid == 0:
            mid = 0

        ticks = [xaxis.lim[0], mid, xaxis.lim[1]]

    if ticklabels is None:
        ticklabels = ticks

    if steps is None:
        steps = cmap.N // 2

    if isinstance(steps, int):
        steps = np.array(list(range(0, steps)))
        steps = steps / (steps.size - 1) * \
            (norm.vmax - norm.vmin) + norm.vmin

    svg.add_rect(x=x, y=y, w=w, h=h, fill=svgplot.rgbtohex(cmap(0)))
    svg.add_rect(x=x+w/4, y=y, w=w/2, h=h, fill=svgplot.rgbtohex(
        cmap((cmap.N-1 if cmap.N % 2 == 0 else cmap.N)//2)))

    for step in steps:
        xoff = xaxis.scale(step)
        w1 = w - xoff
        col = svgplot.rgbtohex(cmap(int(norm(step) * cmap.N - 1)))
        svg.add_rect(x=x+xoff, y=y, w=w1, h=h, fill=col)
        #self.add_line(x1=x+xoff, y1=y, x2=x+xoff, y2=y+h)

    # for step in reversed(steps[0:steps.size//2]):
    #     xoff = xaxis.scale(step)
    #     w1 = xoff #w/2 - xoff
    #     col = svgplot.rgbtohex(cmap(int(norm(step) * cmap.N - 1)))
    #     self.add_rect(x=x, y=y, w=w1, h=h, fill=col)
    #     #self.add_line(x1=x+xoff, y1=y, x2=x+xoff, y2=y+h)

    #     print(step, col, w1)

    # for step in steps[steps.size//2:]:
    #     xoff = xaxis.scale(step)
    #     w1 = w - xoff #w/2 - xoff
    #     col = svgplot.rgbtohex(cmap(int(norm(step) * cmap.N - 1)))
    #     self.add_rect(x=x+xoff, y=y, w=w1, h=h, fill=col)

    if showaxis:
        graph.add_x_axis(svg,
                         pos=(x, y+h+5),
                         axis=xaxis,
                         ticks=ticks,
                         ticklabels=ticklabels,
                         showticks=True,
                         showline=False)

    if showframe:
        svg.add_frame(x, y=y, w=w, h=h, stroke=stroke)


def add_vert_colorbar(svg,
                      x=0,
                      y=0,
                      w=25,
                      h=200,
                      steps=None,
                      cmap=matplotlib.cm.viridis,
                      ticks=None,
                      ticklabels=None,
                      axis=None,
                      norm=None,
                      showframe=True,
                      showaxis=True,
                      stroke=2,
                      align='c'):    

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
        steps = cmap.N // 2

    if isinstance(steps, int):
        steps = np.array(list(range(0, steps)))
        steps = steps / (steps.size - 1) * \
            (norm.vmax - norm.vmin) + norm.vmin

    #self.add_rect(x=x, y=y, w=w, h=h, fill=svgplot.rgbtohex(cmap(0)))
    #self.add_rect(x=x, y=y+h/4, w=w, h=h/2, fill=svgplot.rgbtohex(cmap((cmap.N-1 if cmap.N % 2 == 0 else cmap.N)//2)))

    for step in steps:
        yoff = axis.scale(step)
        h1 = h - yoff
        col = svgplot.rgbtohex(cmap(int(norm(step) * cmap.N - 1)))
        svg.add_rect(x=x, y=y, w=w, h=h1, fill=col)
        #self.add_line(x1=x+xoff, y1=y, x2=x+xoff, y2=y+h)

        # if step == 4:
        #    break

    # for step in reversed(steps[0:steps.size//2]):
    #     xoff = xaxis.scale(step)
    #     w1 = xoff #w/2 - xoff
    #     col = svgplot.rgbtohex(cmap(int(norm(step) * cmap.N - 1)))
    #     self.add_rect(x=x, y=y, w=w1, h=h, fill=col)
    #     #self.add_line(x1=x+xoff, y1=y, x2=x+xoff, y2=y+h)

    #     print(step, col, w1)

    # for step in steps[steps.size//2:]:
    #     xoff = xaxis.scale(step)
    #     w1 = w - xoff #w/2 - xoff
    #     col = svgplot.rgbtohex(cmap(int(norm(step) * cmap.N - 1)))
    #     self.add_rect(x=x+xoff, y=y, w=w1, h=h, fill=col)

    if showaxis:
        graph.add_y_axis(svg, x=x+w,
                         y=0,
                         axis=axis,
                         ticks=ticks,
                         ticklabels=ticklabels,
                         showticks=True,
                         showline=False,
                         side='r')

    if showframe:
        svg.add_frame(x, y=y, w=w, h=h, stroke=stroke)
