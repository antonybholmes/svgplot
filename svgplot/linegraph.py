from typing import Mapping, Optional, Union
from .axis import Axis
from .svgfigure import SVGFigure
from . import graph

def add_linegraph(svg: SVGFigure,
                  data,
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
                  fill_opacity: float = 0.2):
    if axes is None:
        axes = (Axis(lim=(0, 100), w=200), Axis(lim=(0, 100), w=200))

    x, y = pos
    xaxis, yaxis = axes

    # set some defaults
    _show_axes = graph._get_default_axes_kws(xaxis_kws, yaxis_kws)

    points = []

    # ensure points go from bottom of axis to make fill work
    if fill != 'none':
        if data.iloc[0, 1] != yaxis.lim[0]:
            #points = [[x + xaxis.scale(data.iloc[0, 0]), y + yaxis.trans(yaxis.lim[0], clip=_show_axes[1]['clip'])]]

            if _show_axes[1]['invert']:
                points = [
                    [x + xaxis.scale(data.iloc[0, 0]), y + yaxis.scale(yaxis.lim[0], clip=_show_axes[1]['clip'])]]
            else:
                points = [[x + xaxis.scale(data.iloc[0, 0]), y + yaxis.w -
                           yaxis.scale(yaxis.lim[0], clip=_show_axes[1]['clip'])]]

            # pass

    used = set()

    # leading edge
    if isinstance(data, list):
        for d in data:
            id = f'{d[0]}:{d[1]}'

            if id in used:
                continue

            used.add(id)

            if _show_axes[1]['invert']:
                points.append([x + xaxis.scale(d[0]), y +
                              yaxis.scale(d[1], clip=_show_axes[1]['clip'])])
            else:
                points.append([x + xaxis.scale(d[0]), y + yaxis.w -
                              yaxis.scale(d[1], clip=_show_axes[1]['clip'])])
    else:
        for i in range(0, data.shape[0]):
            id = f'{data.iloc[i, 0]}:{data.iloc[i, 1]}'

            if id in used:
                continue

            used.add(id)

            if _show_axes[1]['invert']:
                points.append([x + xaxis.scale(data.iloc[i, 0]), y +
                              yaxis.scale(data.iloc[i, 1], clip=_show_axes[1]['clip'])])
            else:
                points.append([x + xaxis.scale(data.iloc[i, 0]), y + yaxis.w -
                              yaxis.scale(data.iloc[i, 1], clip=_show_axes[1]['clip'])])

    # make fill neater
    if fill != 'none':
        if data.iloc[-1, 1] != yaxis.lim[0]:
            if _show_axes[1]['invert']:
                points.append([x + xaxis.scale(data.iloc[-1, 0]), y +
                              yaxis.scale(yaxis.lim[0], clip=_show_axes[1]['clip'])])
            else:
                points.append([x + xaxis.scale(data.iloc[-1, 0]), y + yaxis.w -
                              yaxis.scale(yaxis.lim[0], clip=_show_axes[1]['clip'])])

    svg.add_polyline(points, color=color,
                     stroke=stroke, fill=fill,
                     fill_opacity=fill_opacity)

    # label axes

    if title is not None:
        svg.add_text_bb(title, x=xaxis.w/2, y=y-40, align='c')

    #graph.add_axes(svg, pos=pos, axes=axes, xaxis_kws=xaxis_kws, yaxis_kws=yaxis_kws)

    return xaxis.w, yaxis.w