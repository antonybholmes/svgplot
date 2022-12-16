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

class MedianStyle(Enum):
    LINE = 0
    CIRCLE = 1

def _add_boxplot(svg: SVGFigure,
                 data_points: np.array,
                 axes: tuple[Axis, Axis],
                 width: int = 18,
                 whisker_width: Optional[int] = None,
                 color: str = 'blue',
                 fill: str = 'white',
                 opacity: float = 1,
                 stroke=3,
                 pos: tuple[int, int] = (0, 0),
                 median_style: MedianStyle = MedianStyle.CIRCLE,
                 dot_size: int = 12,
                 rounded: bool = True):

    if whisker_width is None:
        whisker_width = width

    x, y = pos

    _, yaxis = axes

    q1, median, q3 = np.quantile(data_points, [0.25, 0.5, 0.75])

    iqr = q3 - q1
    iqr_15 = 1.5 * iqr
    q1_iqr = max(q1 - iqr_15, data_points.min())
    q3_iqr = min(q3 + iqr_15, data_points.max())

    #svg.add_rect(x=x-iqr_15_line_width/2, y=y+yaxis.w-yaxis.scale(q3_iqr), w=iqr_15_line_width, h=yaxis.scale(q3_iqr) - yaxis.scale(q1_iqr), fill='red', rounding=iqr_15_line_width)
    #svg.add_rect(x=x-iqr_line_width/2, y=y+yaxis.w-yaxis.scale(q3), w=iqr_line_width, h=yaxis.scale(q3) - yaxis.scale(q1), fill='red', rounding=iqr_line_width)

    #svg.add_rect(x=x-iqr_15_line_width/2, y=y+yaxis.w-yaxis.scale(q3_iqr), w=iqr_15_line_width, h=yaxis.scale(q3_iqr) - yaxis.scale(q1_iqr), color='black', fill='white', stroke=2)

    svg.add_line(x1=x, y1=y + yaxis.w-yaxis.scale(q3_iqr), y2=y +
                 yaxis.w-yaxis.scale(q1_iqr), color=color, stroke=stroke)
    svg.add_line(x1=x-whisker_width/2, x2=x+whisker_width/2, y1=y +
                 yaxis.w-yaxis.scale(q3_iqr), color=color, stroke=stroke)
    svg.add_line(x1=x-whisker_width/2, x2=x+whisker_width/2, y1=y +
                 yaxis.w-yaxis.scale(q1_iqr), color=color, stroke=stroke)

    #svg.add_rect(x=x-iqr_line_width/2, y=y+yaxis.w-yaxis.scale(q3), w=iqr_line_width, h=yaxis.scale(q3)-yaxis.scale(median), fill='white', color=color, stroke=stroke, rounding=iqr_line_width/2)
    #svg.add_rect(x=x-iqr_line_width/2, y=y+yaxis.w-yaxis.scale(median), w=iqr_line_width, h=yaxis.scale(median)-yaxis.scale(q1), fill='white', color=color, stroke=stroke, rounding=iqr_line_width/2)

    svg.add_rect(x=x-width/2, y=y+yaxis.w-yaxis.scale(q3), w=width, h=yaxis.scale(
        q3) - yaxis.scale(q1), stroke=stroke, fill=fill, fill_opacity=opacity, color=color, rounding=min(10, width/2) if rounded else 0)

    y1 = y+yaxis.w-yaxis.scale(median)

    match median_style:
        case MedianStyle.CIRCLE:
            svg.add_circle(x=x, y=y1, w=dot_size, fill=color)
        case _:
            svg.add_line(x1=x-width/2, x2=x+width/2, y1=y1, color=color)





def add_boxplot(svg: SVGFigure,
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
                swarm_kws: Optional[dict[str, Any]] = None,
                box_kws: Optional[dict[str, Any]] = None) -> None:

    _x_kws = core.kws({'show': True, 'show_labels': True, 'show_axis': True,
                      'label_pos': 'axis', 'label_orientation': 'h'}, x_kws)
    _y_kws = core.kws({'show': True, 'lim': None, 'ticks': None,
                       'ticklabels': None, 'offset': None, 'title': None}, y_kws)
    _swarm_kws = core.kws({'show': True, 'dot_size': 10,
                          'opacity': 0.7, 'style': swarm.PlotStyle.TRIANGLE}, swarm_kws)
    _box_kws = core.kws({'show': True, 'width': 20, 'whisker_width': 20, 'stroke': 3, 'dot_size': 12,
                         'fill': 'white', 'opacity': 1, 'rounded': True, 'median_style': MedianStyle.CIRCLE}, box_kws)

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

            if _box_kws['show']:
                _add_boxplot(svg,
                             dp,
                             axes=(xaxis, yaxis),
                             width=_box_kws['width'],
                             whisker_width=_box_kws['whisker_width'],
                             color=color,
                             median_style=_box_kws['median_style'],
                             dot_size=_box_kws['dot_size'],
                             fill=_box_kws['fill'],
                             opacity=_box_kws['opacity'],
                             stroke=_box_kws['stroke'],
                             pos=(x2, y1),
                             rounded=_box_kws['rounded'])

            x2 += plot_width  # 2 * xaxis.w
            colori += 1

        x2 += x_gap

    if _x_kws['show_axis']:
        svg.add_line(x1=pos[0]-plot_width/2-x_gap, x2=x2 -
                     plot_width/2-x_gap, y1=y1+yaxis.w)

    if show_legend:
        swarm._add_legend(svg,
                    hue_order,
                    palette,
                    pos=(x2-plot_width+40, 0))

    return (x2 - x_gap - plot_width, height)
