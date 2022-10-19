import numpy as np
from typing import Mapping, Optional, Union
from .axis import Axis
from .svgfigure import SVGFigure
from . import graph
from scipy.interpolate import make_interp_spline
from scipy import interpolate
from scipy import ndimage
from pandas import DataFrame

def add_linegraph(svg: SVGFigure,
                  data: DataFrame,
                  pos: tuple[float, float] = (0, 0),
                  stroke: int = 4,
                  title: Optional[str] = '',
                  axes: tuple[Axis, Axis] = None,
                  xaxis_kws: Union[bool, str, Mapping[str,
                                                               Union[int, float, str, bool]]] = {},
                  yaxis_kws: Union[bool, str, Mapping[str,
                                                               Union[int, float, str, bool]]] = {},
                  color: str = 'black',
                  fill: str = 'none',
                  fill_opacity: float = 0.2,
                  smooth=False):
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
    if axes is None:
        axes = (Axis(lim=(0, 100), w=200), Axis(lim=(0, 100), w=200))

    x, y = pos
    xaxis, yaxis = axes

    # set some defaults
    _show_axes = graph._get_default_axes_kws(xaxis_kws, yaxis_kws)

    xd = data.iloc[:, 0].values
    yd = data.iloc[:, 1].values


    if fill != 'none':
        yd[0] = yaxis.lim[0]
        yd[-1] = yaxis.lim[0]

    if smooth:
        print(np.where(np.isnan(xd)))
        print('h', np.where(np.isnan(yd)))

        #X_Y_Spline = make_interp_spline(xd, yd)
 
        # Returns evenly spaced numbers
        # over a specified interval.
        #x_smooth = np.linspace(xd.min(), xd.max(), 500)
        #y_smooth = X_Y_Spline(x_smooth)

        #spl = interpolate.UnivariateSpline(xd, yd)

        #xd = x_smooth
        #yd = spl(xd)

        sigma = 2
        x_g1d = ndimage.gaussian_filter1d(xd, sigma)
        y_g1d = ndimage.gaussian_filter1d(yd, sigma)
        
        y_g1d[0] = yd[0]
        y_g1d[-1] = yd[-1]

        xd = x_g1d
        yd = y_g1d

        #yd[0] = yaxis.lim[0]
        #yd[-1] = yaxis.lim[0]

        #xd = X_
        #yd = Y_

    points = []

    # ensure points go from bottom of axis to make fill work
    # if fill != 'none':
    #     if yd[0] != yaxis.lim[0]:
    #         #points = [[x + xaxis.scale(data.iloc[0, 0]), y + yaxis.trans(yaxis.lim[0], clip=_show_axes[1]['clip'])]]

    #         if _show_axes[1]['invert']:
    #             points = [
    #                 [x + xaxis.scale(xd[0]), y + yaxis.scale(yaxis.lim[0], clip=_show_axes[1]['clip'])]]
    #         else:
    #             points = [[x + xaxis.scale(xd[0]), y + yaxis.w -
    #                        yaxis.scale(yaxis.lim[0], clip=_show_axes[1]['clip'])]]

    #         # pass

    used = set()

    # leading edge
    # if isinstance(data, list):
    #     for d in data:
    #         id = f'{d[0]}:{d[1]}'

    #         if id in used:
    #             continue

    #         used.add(id)

    #         if _show_axes[1]['invert']:
    #             points.append([x + xaxis.scale(d[0]), y +
    #                           yaxis.scale(d[1], clip=_show_axes[1]['clip'])])
    #         else:
    #             points.append([x + xaxis.scale(d[0]), y + yaxis.w -
    #                           yaxis.scale(d[1], clip=_show_axes[1]['clip'])])
    # else:
    for i in range(xd.size):
        id = f'{xd[i]}:{yd[i]}'

        if id in used:
            continue

        used.add(id)

        if _show_axes[1]['invert']:
            points.append([x + xaxis.scale(xd[i]), y +
                            yaxis.scale(yd[i], clip=_show_axes[1]['clip'])])
        else:
            points.append([x + xaxis.scale(xd[i]), y + yaxis.w -
                            yaxis.scale(yd[i], clip=_show_axes[1]['clip'])])

    # make fill neater
    # if fill != 'none':
    #     if yd[-1] != yaxis.lim[0]:
    #         if _show_axes[1]['invert']:
    #             points.append([x + xaxis.scale(xd[-1]), y +
    #                           yaxis.scale(yaxis.lim[0], clip=_show_axes[1]['clip'])])
    #         else:
    #             points.append([x + xaxis.scale(xd[-1]), y + yaxis.w -
    #                           yaxis.scale(yaxis.lim[0], clip=_show_axes[1]['clip'])])

    svg.add_polyline(points, color=color,
                     stroke=stroke, fill=fill,
                     fill_opacity=fill_opacity)

    # label axes

    if title is not None:
        svg.add_text_bb(title, x=xaxis.w/2, y=y-40, align='c')

    #graph.add_axes(svg, pos=pos, axes=axes, xaxis_kws=xaxis_kws, yaxis_kws=yaxis_kws)

    return xaxis.w, yaxis.w