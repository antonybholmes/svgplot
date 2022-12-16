from enum import Enum
from typing import Any, Optional
import numpy as np
from pandas import DataFrame
import matplotlib
from .svgfigure import SVGFigure
from .axis import Axis
from . import core
from . import swarm
from . import graph

class PlotStyle(Enum):
    CIRCLE = 0
    TRIANGLE = 1
    CROSS = 2

def _add_legend(svg: SVGFigure,
                hue_order: Optional[list[str]] = None,
                colors: Optional[list[str]] = None,
                pos: tuple[int, int] = (0, 0)):
    x, y = pos

    for huei, hue in enumerate(hue_order):
        svg.add_bullet(
            hue, x=x, y=y, color=colors[huei % colors.size], shape='s')
        y += 50


def _add_swarm(svg: SVGFigure,
               data_points: np.array,
               axes: tuple[Axis, Axis],
               dot_size: int = 8,
               color: str = 'blue',
               fill: Optional[str] = None,
               opacity: float = 0.3,
               pos: tuple[int, int] = (0, 0),
               style: PlotStyle = PlotStyle.CIRCLE):
    """Add a swarm plot

    Args:
        svg (SVGFigure): _description_
        data_points (np.array): _description_
        axes (tuple[Axis, Axis]): _description_
        dot_size (int, optional): _description_. Defaults to 8.
        color (str, optional): _description_. Defaults to 'blue'.
        fill (Optional[str], optional): _description_. Defaults to None.
        opacity (float, optional): _description_. Defaults to 0.3.
        pos (tuple[int, int], optional): _description_. Defaults to (0, 0).
        style (str, optional): _description_. Defaults to '.'.
    """               
    if fill is None:
        fill = color

    x, y = pos

    xaxis, yaxis = axes

    dot_r = dot_size / 2

    dot_positions = [y + yaxis.w - yaxis.scale(p) for p in sorted(data_points)]

    groups = []

    x_lim = [x - xaxis.w, x + xaxis.w]

    for p in dot_positions:
        found = False

        p1 = p - dot_r
        p2 = p + dot_r

        for group in groups:
            if (p1 >= group['x1'] and p1 <= group['x2']) or (p2 >= group['x1'] and p2 <= group['x2']):
                group['dots'].append(p)
                # make group more inclusive
                #group['x1'] = min(group['x1'], p1)
                #group['x2'] = max(group['x2'], p2)
                found = True
                break

        if not found:
            groups.append({'x1': p1, 'x2': p2, 'dots': [p]})

    for group in groups:
        x2 = x - (len(group['dots']) - 1) * dot_size / 2
        l = (len(group['dots']) - 1) * dot_size
        # shift points

        # prevent dots from expanding beyond confines of plot
        
        
        #if x3 != x2:
        #print(x2, x3, x_lim, l)

        for i, p in enumerate(reversed(group['dots'])):
            x3 = max(x_lim[0], min(x_lim[1], x2))

            match style:
                case PlotStyle.CROSS:
                    svg.add_line(x1=x3-dot_size/2, x2=x3+dot_size/2, y1=p, color=color)
                    svg.add_line(x1=x3, y1=p-dot_size/2, y2=p+dot_size/2, color=color)
                case PlotStyle.TRIANGLE:
                    h = np.sin(np.pi / 3) * dot_size
                    svg.add_polygon([[x3-dot_size/2, p+h/2], [x3, p-h/2], [x3+dot_size/2, p+h/2]], fill=fill, fill_opacity=opacity)
                case _:
                    svg.add_circle(x=x3, y=p, w=dot_size,
                                fill=fill, fill_opacity=opacity)

            if i % 2 == 0:
                x2 += l
            else:
                x2 -= l

            l -= dot_size


def add_swarm(svg: SVGFigure,
                data: DataFrame,
                x: str = '',
                y: str = '',
                hue: Optional[str] = None,
                x_order: Optional[list[str]] = None,
                hue_order: Optional[list[str]] = [''],
                palette: Optional[list[str]] = None,
                plot_width: int = 80,
                height: int = 500,
                x_gap: int = 20,
                title_offset: int = -50,
                show_legend: bool = False,
                pos: tuple[int, int] = (0, 0),
                x_kws: Optional[dict[str, Any]] = None,
                y_kws: Optional[dict[str, Any]] = None,
                swarm_kws: Optional[dict[str, Any]] = None) -> None:

    _x_kws = core.kws({'show': True, 'show_labels': True, 'show_axis': True,
                      'label_pos': 'axis', 'label_orientation': 'h'}, x_kws)
    _y_kws = core.kws({'show': True, 'lim': None, 'ticks': None,
                       'ticklabels': None, 'offset': None, 'title': None}, y_kws)
    _swarm_kws = core.kws({'show': True, 'dot_size': 10,
                          'opacity': 0.7, 'style': swarm.PlotStyle.TRIANGLE}, swarm_kws)
                          
    if palette is None:
        palette = matplotlib.cm.Set2

    if isinstance(palette, matplotlib.colors.ListedColormap):
        palette = [core.rgbtohex(c) for c in palette.colors]

    if isinstance(palette, list):
        palette = np.array(palette)

    if hue is not None:
        palette = palette[0:2]

    if x_order is None:
        x_order = []
        used = set()

        for n in data[x]:
            if n in used:
                continue

            x_order.append(n)
            used.add(n)

    x_order = np.array(x_order)

    if hue_order is None:
        hue_order = []
        used = set()

        for n in data[hue]:
            if n in used:
                continue

            hue_order.append(n)
            used.add(n)

    hue_order = np.array(hue_order)

    x1, y1 = pos

    if _y_kws['lim'] is None:
        _y_kws['lim'] = (data[y].min(), data[y].max())

    if _y_kws['offset'] is None:
        _y_kws['offset'] = -(plot_width/2 + x_gap)

    if _y_kws['title'] is None:
        _y_kws['title'] = y

    xaxis = Axis(lim=[0, 1], w=plot_width/2)
    yaxis = Axis(lim=_y_kws['lim'], ticks=_y_kws['ticks'],
                 ticklabels=_y_kws['ticklabels'], label=_y_kws['title'], w=height)

    if _y_kws['show']:
        graph.add_y_axis(svg, axis=yaxis, pos=(_y_kws['offset'], 0))

    data_points = []

    for labeli, x_label in enumerate(x_order):
        for huei, hue_label in enumerate(hue_order):
            if hue_label != '':
                d = data[(data[x] == x_label) & (data[hue] == hue_label)][y]
            else:
                d = data[data[x] == x_label][y]

            data_points.append(d)

    colori = 0

    x2 = x1
    w = (hue_order.size - 1) * plot_width

    for labeli, label in enumerate(x_order):
        if _x_kws['show_labels']:
            match _x_kws['label_pos']:
                case 'title':
                    svg.add_text_bb(label, x=x2+w/2, y=title_offset, align='c')
                case _:
                    if _x_kws['label_orientation'] == 'v':
                        svg.add_text_bb(label, x=x2+w/2, y=y1 +
                                        yaxis.w+10, orientation='v', align='r')
                    else:
                        svg.add_text_bb(label, x=x2+w/2, y=y1 +
                                        yaxis.w+50, align='c')

        for huei, hue_label in enumerate(hue_order):
            x2 += plot_width  # 2 * xaxis.w
            colori += 1

        x2 += x_gap

    colori = 0
    x2 = x1

    for labeli, label in enumerate(x_order):
        for huei, hue_label in enumerate(hue_order):
            color = palette[colori % palette.size]

            dp = data_points[colori]

            if _swarm_kws['show']:
                swarm._add_swarm(svg,
                                 dp,
                                 axes=(xaxis, yaxis),
                                 dot_size=_swarm_kws['dot_size'],
                                 color=color,
                                 opacity=_swarm_kws['opacity'],
                                 pos=(x2, y1),
                                 style=_swarm_kws['style'])

            x2 += plot_width  # 2 * xaxis.w
            colori += 1

        x2 += x_gap

    if _x_kws['show_axis']:
        svg.add_line(x1=pos[0]-plot_width/2-x_gap, x2=x2 -
                     plot_width/2-x_gap, y1=y1+yaxis.w)

    if show_legend:
        _add_legend(svg,
                    hue_order,
                    palette,
                    pos=(x2-plot_width+40, 0))

    return (x2 - x_gap - plot_width, height)