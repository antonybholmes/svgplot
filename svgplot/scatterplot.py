from optparse import Option
from typing import Mapping, Optional, Union
import numpy as np
import matplotlib
from . import axis
from .svgfigure import SVGFigure
from . import graph
from . import legend

DEFAULT_COLORS = matplotlib.colormaps['tab10'].colors


def add_scatterplot(svg: SVGFigure,
                    data,
                    x: str,
                    y: str,
                    hue: Optional[Union[str, list[str]]] = None,
                    hue_order: list[str] = [],
                    palette: Union[str, Mapping[str, str]] = DEFAULT_COLORS,
                    size: Optional[Union[str, list[str]]] = None,
                    size_order: list[str] = [],
                    sizes: Union[int, str, Mapping[str, int]] = 20,
                    title: str = '',
                    pos: tuple[int, int] = (0, 0),
                    dim: tuple[int, int] = (500, 500),
                    axes: tuple[axis.Axis, axis.Axis] = None,
                    xaxis_kws: Mapping[str, Union[int, float, str, bool]] = {},
                    yaxis_kws: Mapping[str, Union[int, float, str, bool]] = {},
                    show_legend: bool = False,
                    outline: bool = False):

    if isinstance(hue, str):
        if hue == '.index':
            hue = data.index.values
        else:
            hue = data[hue].values
            print('hue by name', hue)

    if hue is None:
        hue = [''] * data.shape[0]

    hue = np.array(hue)

    # draw alphabetically based on names
    if len(hue_order) == 0:
        hue_order = np.array(sorted(set(hue)))

    hue_idx = {}
    print('hue', 'order')
    for ho in hue_order:
        hue_idx[ho] = np.array([i for i in range(hue.size) if ho == hue[i]])

    if isinstance(size, str):
        if size == '.index':
            size = data.index.values
        else:
            size = data[size].values

    if size is None:
        size = [''] * data.shape[0]

    size = np.array(size)

    if len(size_order) == 0:
        size_order = np.array(sorted(set(size)))

    if isinstance(sizes, int):
        sizes = {so: size for so in size_order}
    elif isinstance(sizes, list):
        sizes = {so: sizes[i % len(sizes)] for i, so in enumerate(size_order)}
    else:
        pass

    if not isinstance(sizes, dict):
        raise Exception("sizes must be a dict")
    
    if isinstance(palette, str):
        palette = {ho: palette for ho in hue_order}
    elif isinstance(palette, list):
        palette = {ho: palette[i % len(palette)]
                  for i, ho in enumerate(hue_order)}
    else:
        pass

    if not isinstance(palette, dict):
        raise Exception("colors must be a dict")

    # if isinstance(fill_opacity, str):
    #     opacity = {ho:fill_opacity for ho in hue_order}
    # elif isinstance(fill_opacity, list):
    #     opacity = {ho:palette[i % len(fill_opacity)] for i, ho in enumerate(hue_order)}
    # elif isinstance(fill_opacity, dict):
    #     opacity = fill_opacity
    # else:
    #     opacity = {ho:1 for ho in hue_order}

    if axes is None:
        xaxis = axis.auto_axis(
            lim=[data[x].min(), data[x].max()], w=dim[0], label=x)
        yaxis = axis.auto_axis(
            lim=[data[y].min(), data[y].max()], w=dim[1], label=y)
    else:
        xaxis, yaxis = axes

    # set some axis display props
    _show_axes = graph._get_default_axes_kws(xaxis_kws, yaxis_kws)

    for ho in hue_order:

        idx = hue_idx[ho]
        print('oh', ho, idx)
        d_x = data[x].values[idx]
        d_y = data[y].values[idx]

        hue_size = size[idx]

        points = []

        for i, px in enumerate(d_x):
            py = d_y[i]

            px = pos[0] + xaxis.scale(px, clip=_show_axes[0]['clip'])

            if _show_axes[1]['invert']:
                py = pos[1] + yaxis.scale(py, clip=_show_axes[1]['clip'])
            else:
                py = pos[1] + yaxis.w - \
                    yaxis.scale(py, clip=_show_axes[1]['clip'])

            points.append([px, py])

        points = np.array(points)

        for i, p in enumerate(points):
            # size label for this point
            phs = hue_size[i]

            # get size from lookup in sizes
            point_size = sizes[phs]

            print('cheese', i, phs, point_size)

            svg.add_circle(x=p[0], y=p[1], w=point_size, fill=palette[ho])

            if outline:
                svg.add_circle(x=p[0], y=p[1], w=point_size, color='black')

    # label axes

    if title is not None:
        svg.add_text_bb(title, x=xaxis.w/2, y=pos[1]-40, align='c')

    graph.add_axes(svg, pos=pos, axes=(xaxis, yaxis),
                   xaxis_kws=xaxis_kws, yaxis_kws=yaxis_kws)

    if show_legend:
        legend.add_legend(svg,
                          hue_order=hue_order,
                          palette=palette,
                          pos=(pos[0] + xaxis.w - 100, pos[1]))

    return {'w': xaxis.w, 'h': yaxis.w, 'xaxis': xaxis, 'yaxis': yaxis}
