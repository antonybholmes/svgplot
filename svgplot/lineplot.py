import numpy as np
from typing import Mapping, Optional, Union
from .axis import Axis
from .svgfigure import SVGFigure
from . import graph
from scipy.interpolate import CubicSpline
from scipy import ndimage
from pandas import DataFrame


def add_lineplot(svg: SVGFigure,
                 data: DataFrame,
                 x: Optional[str] = None,
                 y: Optional[str] = None,
                 hue: Optional[str] = None,
                 hue_order: Optional[str] = None,
                 palette: dict[str, str] = {},
                 pos: tuple[float, float] = (0, 0),
                 stroke: int = 4,
                 title: Optional[str] = '',
                 axes: tuple[Axis, Axis] = None,
                 xaxis_kws: Mapping[str, Union[int, float, str, bool]] = {},
                 yaxis_kws: Mapping[str, Union[int, float, str, bool]] = {},
                 color: str = 'black',
                 fill: str = 'none',
                 fill_opacity: float = 0.2,
                 smooth_kws: Mapping[str, Union[int, float, str, bool]] = {},):
    """_summary_

    Args:
            svg (SVGFigure): _description_
            data (DataFrame): _description_
            pos (tuple[float, float], optional): _description_. Defaults to (0, 0).
            stroke (int, optional): _description_. Defaults to 4.
            title (Optional[str], optional): _description_. Defaults to ''.
            axes (tuple[Axis, Axis], optional): _description_. Defaults to None.
            xaxis_kws (Union[bool, str, Mapping[str, Union[int, float, str, bool]]], optional): _description_. Defaults to {}.
            yaxis_kws (Union[bool, str, Mapping[str, Union[int, float, str, bool]]], optional): _description_. Defaults to {}.
            color (str, optional): _description_. Defaults to 'black'.
            fill (str, optional): _description_. Defaults to 'none'.
            fill_opacity (float, optional): _description_. Defaults to 0.2.
            smooth (bool, optional): _description_. Defaults to False.

    Returns:
            _type_: _description_
    """
    # set some defaults
    _show_axes = graph._get_default_axes_kws(xaxis_kws, yaxis_kws)

    _smooth_kws = {'smooth': False, 'steps': 200, 'zero_ends':True}
    _smooth_kws.update(smooth_kws)

    xp, yp = pos
    xaxis, yaxis = axes

    if x is None:
        x = ''

    if y is None:
        y = ''

    if hue is None:
        hue = ''

    if hue_order is None:
        if hue != '':
            hue_order = sorted(data[hue].unique())
        else:
            hue_order = ['']  # sorted(data[x].unique())

    hue_order = np.array(hue_order)

    for ho in hue_order:
        if ho != '':
            dfx = data[data[hue] == ho]
        else:
            dfx = data

        if x != '':
            xd = data[x].values
        else:
            xd = data.iloc[:, 0].values

        if y != '':
            yd = data[y].values
        else:
            yd = data.iloc[:, 1].values

        if _smooth_kws['smooth']:
            cs = CubicSpline(xd, yd)
            # np.linspace(x_sm.min(), x_sm.max(), 200)
            xd = np.linspace(xaxis.lim[0], xaxis.lim[1], _smooth_kws['steps'])
            yd = cs(xd)  # spline(x, y, x_smooth)



        points = []

        used = set()

        for xi, xs in enumerate(xd):
            id = f'{xs}:{yd[xi]}'

            if id in used:
                continue

            used.add(id)

            if _show_axes[1]['invert']:
                points.append([xp + xaxis.scale(xs), yp +
                               yaxis.scale(yd[xi], clip=_show_axes[1]['clip'])])
            else:
                points.append([xp + xaxis.scale(xs), yp + yaxis.w -
                               yaxis.scale(yd[xi], clip=_show_axes[1]['clip'])])

        if _smooth_kws['zero_ends'] or fill != 'none':
            points[0][1] = yp + yaxis.w
            points[-1][1] = points[0][1]

        if ho in palette:
            color = palette[ho]
        else:
            color = 'black'
                
        svg.add_polyline(points, color=color, stroke=stroke,
                         fill=fill, fill_opacity=fill_opacity)

    # label axes

    if title is not None:
        svg.add_text_bb(title, x=xaxis.w/2, y=yp-40, align='c')

    graph.add_axes(svg, pos=pos, axes=axes,
                   xaxis_kws=xaxis_kws, yaxis_kws=yaxis_kws)

    return xaxis.w, yaxis.w
