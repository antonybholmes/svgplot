from typing import Mapping, Optional, Union, Any
from .axis import Axis
from .svgfigure import SVGFigure
from . import svgfiguredraw
import numpy as np
import math
from . import graph
from .lineplot import add_lineplot
from . import hatch as phatch
from .axis import Axis
from enum import Enum
import pandas as pd
from scipy.interpolate import CubicSpline


def add_histplot(svg: SVGFigure,
                 data: pd.DataFrame,
                 axes: tuple[Axis, Axis],
                 x: Optional[str] = None,
                 hue: Optional[str] = None,
                 hue_order: Optional[list[str]] = None,
                 palette: dict[str, str] = {},
                 opacity: dict[str, float] = {},
                 bins: int = 70,
                 pos: tuple[int, int] = (0, 0),
                 bar_color: str = '#AACCFF',
                 bar_blend: bool = True,
                 show_bars: bool = True,
                 xaxis_kws: Mapping[str, Union[int, float, str, bool]] = {},
                 yaxis_kws: Mapping[str, Union[int, float, str, bool]] = {},
                 line_kws: Mapping[str, Union[int, float, str, bool]] = {},
                 title: Optional[str] = None):
    """_summary_

    Args:
        svg (SVGFigure): _description_
        data (pd.DataFrame): _description_
        axes (tuple[Axis, Axis]): _description_
        x (Optional[str], optional): _description_. Defaults to None.
        hue (Optional[str], optional): _description_. Defaults to None.
        hue_order (Optional[list[str]], optional): _description_. Defaults to None.
        palette (dict[str, str], optional): _description_. Defaults to {}.
        opacity (dict[str, float], optional): _description_. Defaults to {}.
        bins (int, optional): _description_. Defaults to 70.
        pos (tuple[int, int], optional): _description_. Defaults to (0, 0).
        bar_color (str, optional): _description_. Defaults to '#AACCFF'.
        bar_blend (bool, optional): Overlaps bars to remove white line artifacts. If using transparent colors, 
                                    you may want to turn this off. Defaults to True.
        show_bars (bool, optional): _description_. Defaults to True.
        show_smoothed (bool, optional): Overlay a smoothed line over the bars. Defaults to True.
        title (Optional[str], optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """

    xp, yp = pos
    xaxis, yaxis = axes

    _line_kws = {'show':False, 'fill':False, 'smooth': True}
    _line_kws.update(line_kws)

    _show_axes = graph._get_default_axes_kws(xaxis_kws, yaxis_kws)

    #yaxis = Axis(lim=ylim, w=height)

    #w = means.size * block_size

    #xaxis = axis.Axis(lim=[0, df.shape[1]], w=w)

    y2 = yp + yaxis.w

    if x is None:
        x = ''

    if hue is None:
        hue = ''

    if hue_order is None:
        if hue != '':
            hue_order = sorted(data[hue].unique())
        else:
            hue_order = ['']  # sorted(data[x].unique())

    hue_order = np.array(hue_order)

    # draw bars

    x1 = xp

    ret = []

    

    for ho in hue_order:
        if ho != '':
            dfx = data[data[hue] == ho]
        else:
            dfx = data

        color = bar_color
        op = 1

        if ho in opacity:
            op = opacity[ho]

        if ho in palette:
            p = palette[ho]

            if ':' in p:
                color, op = p.split(':')[0:2]
            else:
                color = p

        if x != '':
            dfh = dfx[x].values
        else:
            dfh = dfx.iloc[:, 0].values

        hist, bin_edges = np.histogram(dfh, bins=bins, range=xaxis.lim)
        ret.append([ho, hist, bin_edges])

        

        if show_bars:
            for hi, h in enumerate(hist):
                y1 = y2 - yaxis.scale(h, clip=_show_axes[1]['clip'])
                x2 = x1 + xaxis.scale(bin_edges[hi])
                x3 = x1 + xaxis.scale(bin_edges[hi+1])

                if bar_blend:
                    if hi > 1 and hi < hist.size - 1:
                        # extend width of bars so that white gaps between blocks don't appear.
                        # this fixes svg white line artifacts without affecting the way plot
                        # data is displayed. It is only noticable if you edit the svg.
                        if h <= hist[hi - 1]:
                            # extend a bin back
                            x2 = x1 + xaxis.scale(bin_edges[hi - 1])

                        if h <= hist[hi + 1]:
                            # extend a bin ahead
                            x3 = x1 + xaxis.scale(bin_edges[hi + 2])

                svg.add_rect(x2, y1, x3 - x2, y2 - y1,
                             fill=color, fill_opacity=op)

        if _line_kws['show']:
            dfp = pd.DataFrame()
            dfp['x'] = [(bin_edges[i]+bin_edges[i+1]) /
                        2 for i in range(hist.size)]
            dfp['y'] = hist

            add_lineplot(svg, dfp, x='x', y='y', axes=axes, smooth_kws={
                         'smooth': True}, xaxis_kws={'show': False}, yaxis_kws={'show': False}, fill=color if _line_kws['fill'] else 'none', fill_opacity=op)

            # cs = CubicSpline(bin_edges[0:-1], hist)
            # # np.linspace(x_sm.min(), x_sm.max(), 200)
            # x_smooth = np.linspace(xaxis.lim[0], xaxis.lim[1], 200)
            # y_smooth = cs(x_smooth)  # spline(x, y, x_smooth)

            # used = set()

            # points = []
            # for xi, xs in enumerate(x_smooth):
            #     id = f'{xs}:{y_smooth[xi]}'

            #     if id in used:
            #         continue

            #     used.add(id)
            #     points.append([x1 + xaxis.scale(xs), y2 -
            #                     yaxis.scale(y_smooth[xi], clip=True)])

            # print(points)
            # svg.add_polyline(points, color='black')

    graph.add_x_axis(svg, axis=xaxis, pos=(0, y2))

    graph.add_y_axis(svg, axis=yaxis, pos=(xp, yp))

    if title:
        svg.add_text_bb(title, x=x1+xaxis.w/2, y=-50, align='c')

    return ret
