from optparse import Option
from tkinter.ttk import Style
from turtle import dot
from typing import Any, Mapping, Optional, Union
from scipy.stats import gaussian_kde
from pandas import DataFrame
from .svgfigure import SVGFigure
import matplotlib
import numpy as np
from . import svgplot
from .axis import Axis
from . import graph
from . import boxplot


def _kws(kws: dict[str, Any], user_kws: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    if user_kws is not None:
        kws.update(user_kws)
    return kws


def _add_violin(svg: SVGFigure,
                df: DataFrame,
                max_density: float,
                axes: tuple[Axis, Axis],
                color: str = 'blue',
                opacity: float = 0.3,
                pos: tuple[int, int] = (0, 0)):

    x, y = pos

    xaxis, yaxis = axes

    used = set()

    points1 = []

    for i in range(0, df.shape[0]):
        p = (x - xaxis.scale(df['x'][i]/max_density), y +
             yaxis.w - yaxis.scale(df['y'][i]))

        id = f'{p[0]}:{p[1]}'

        if id in used:
            continue

        used.add(id)

        points1.append(p)

    # if points1[0][0] != x:
    #    points1.insert(0, (x, y + yaxis.w))

    #points1[-1][0] = x

    points1 = np.array(points1)

    points2 = []

    for i in range(points1.shape[0] - 1, -1, -1):
        p = (2*x - points1[i][0], points1[i][1])

        id = f'{p[0]}:{p[1]}'

        if id in used:
            continue

        used.add(id)

        points2.append(p)

    #points2[0][0] = x
    #points2[-1][0] = x

    points2 = np.array(points2)

    points = np.concatenate([points1, points2])

    svg.add_polygon(points, fill=color, fill_opacity=opacity)


def _add_swarm(svg: SVGFigure,
               data_points: np.array,
               axes: tuple[Axis, Axis],
               dot_size: int = 8,
               color: str = 'blue',
               fill: Optional[str] = None,
               opacity: float = 0.3,
               pos: tuple[int, int] = (0, 0),
               style: str = '.'):
    if fill is None:
        fill = color

    x, y = pos

    xaxis, yaxis = axes

    dot_r = dot_size / 2

    dot_positions = [y + yaxis.w - yaxis.scale(p) for p in sorted(data_points)]

    groups = []

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
        l = (len(group['dots'])-1) * dot_size
        # shift points

        for i, p in enumerate(reversed(group['dots'])):
            match style:
                case '+':
                    svg.add_line(x1=x2-dot_size/2, x2=x2+dot_size/2, y1=p, color=color)
                    svg.add_line(x1=x2, y1=p-dot_size/2, y2=p+dot_size/2, color=color)
                case '^':
                    h = np.sin(np.pi / 3) * dot_size
                    svg.add_polygon([[x2-dot_size/2, p+h/2], [x2, p-h/2], [x2+dot_size/2, p+h/2]], fill=fill, fill_opacity=opacity)
                case _:
                    svg.add_circle(x=x2, y=p, w=dot_size,
                                fill=fill, fill_opacity=opacity)

            if i % 2 == 0:
                x2 += l
            else:
                x2 -= l

            l -= dot_size


def _add_legend(svg: SVGFigure,
                hue_order: Optional[list[str]] = None,
                colors: Optional[list[str]] = None,
                pos: tuple[int, int] = (0, 0)):
    x, y = pos

    for huei, hue in enumerate(hue_order):
        svg.add_bullet(
            hue, x=x, y=y, color=colors[huei % colors.size], shape='s')
        y += 50


def _fit_kde(x, bw):
    """Estimate a KDE for a vector of data with flexible bandwidth."""
    kde = gaussian_kde(x, bw)

    # Extract the numeric bandwidth from the KDE object
    bw_used = kde.factor

    # At this point, bw will be a numeric scale factor.
    # To get the actual bandwidth of the kernel, we multiple by the
    # unbiased standard deviation of the data, which we will use
    # elsewhere to compute the range of the support.
    bw_used = bw_used * x.std()

    return kde, bw_used


def _kde_support(x, bw, cut, gridsize=100):
    """Define a grid of support for the violin."""
    d = bw * cut
    support_min = x.min() - d
    support_max = x.max() + d
    return np.linspace(support_min, support_max, gridsize)


def add_violinplot(svg: SVGFigure,
                   data: DataFrame,
                   x: str = '',
                   y: str = '',
                   hue: Optional[str] = None,
                   x_order: Optional[list[str]] = None,
                   hue_order: Optional[list[str]] = None,
                   colors: Optional[list[str]] = None,
                   scale: str = 'area',
                   plot_width: int = 80,
                   height: int = 500,
                   x_gap: int = 20,
                   show_labels: bool = True,
                   label_pos:str='axis',
                   title_offset: int = -50,
                   bw_kws: Optional[dict[str, Any]] = None,
                   show_legend: bool = True,
                   y_kws: Optional[dict[str, Any]] = None,
                   violin_kws: Optional[dict[str, Any]] = None,
                   swarm_kws: Optional[dict[str, Any]] = None,
                   box_kws: Optional[dict[str, Any]] = None) -> None:

    _bw_kws = _kws({'bw': 'scott', 'cut': 2, 'gridsize': 100}, bw_kws)

    _y_kws = _kws({'show': True, 'lim': None, 'ticks': None,
                  'ticklabels': None, 'offset': None}, y_kws)
    _violin_kws = _kws({'show': True, 'opacity': 0.3}, violin_kws)
    _swarm_kws = _kws({'show': True, 'dot_size': 10, 'opacity': 0.7, 'style': '^'}, swarm_kws)
    _box_kws = _kws({'show': True, 'width': 20, 'whisker_width': 20, 'stroke': 3, 'dot_size': 12,
                    'fill': 'white', 'opacity': 1, 'rounded': True, 'median_style': 'circle'}, box_kws)

    if colors is None:
        colors = matplotlib.cm.Set2

    if isinstance(colors, matplotlib.colors.ListedColormap):
        colors = np.array([svgplot.rgbtohex(c) for c in colors.colors])

    if hue is not None:
        colors = colors[0:2]

    if x_order is None:
        x_order = np.sort(data[x].unique())  # data[x][np.sort(idx)]
    else:
        x_order = np.array(x_order)

    if hue_order is None:
        hue_order = np.sort(data[hue].unique())  # data[x][np.sort(idx)]
    else:
        hue_order = np.array(hue_order)

    x1 = y1 = 0

    if _y_kws['lim'] is None:
        _y_kws['lim'] = (data[y].min(), data[y].max())

    if _y_kws['offset'] is None:
        _y_kws['offset'] = -(plot_width + x_gap)

    xaxis = Axis(lim=[0, 1], w=plot_width)
    yaxis = Axis(lim=_y_kws['lim'], ticks=_y_kws['ticks'],
                 ticklabels=_y_kws['ticklabels'], w=height)

    densities = []
    data_points = []

    global_max_density = 0

    colori = 0

    if _y_kws['show']:
        graph.add_y_axis(svg, axis=yaxis, pos=(_y_kws['offset'], 0))

    for labeli, x_label in enumerate(x_order):
        for huei, hue_label in enumerate(hue_order):
            if hue_label != '':
                d = data[(data[x] == x_label) & (data[hue] == hue_label)][y]
            else:
                d = data[data[x] == x_label][y]

            kde, bw_used = _fit_kde(d.values, _bw_kws['bw'])

            x_d = _kde_support(d.values, bw=bw_used,
                               cut=_bw_kws['cut'], gridsize=_bw_kws['gridsize'])

            density = kde.evaluate(x_d)

            df = DataFrame()
            df['x'] = density
            df['y'] = x_d

            densities.append(df)
            data_points.append(d)
            global_max_density = max(global_max_density, density.max())

    colori = 0

    for labeli, label in enumerate(x_order):
        w = 2 * (hue_order.size - 1) * plot_width

        if show_labels:
            match label_pos:
                case 'title':
                    svg.add_text_bb(label, x=x1+w/2, y=title_offset, align='c')
                case _:
                    svg.add_text_bb(label, x=x1+w/2, y=y1+yaxis.w+50, align='c')

        for huei, hue_label in enumerate(hue_order):
            color = colors[colori % colors.size]

            dp = data_points[colori]

            df = densities[colori]

            match scale:
                case 'area':
                    md = global_max_density
                case _:
                    md = df['x'].max()

            if _violin_kws['show']:
                _add_violin(svg,
                            df,
                            md,
                            axes=(xaxis, yaxis),
                            color=color,
                            opacity=_violin_kws['opacity'],
                            pos=(x1, y1))

            # iqr line

            if _swarm_kws['show']:
                _add_swarm(svg,
                           dp,
                           axes=(xaxis, yaxis),
                           dot_size=_swarm_kws['dot_size'],
                           color=color,
                           opacity=_swarm_kws['opacity'],
                           pos=(x1, y1),
                           style=_swarm_kws['style'])

            if _box_kws['show']:
                boxplot.add_boxplot(svg,
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
                                    pos=(x1, y1),
                                    rounded=_box_kws['rounded'])

            x1 += 2 * xaxis.w
            colori += 1

        x1 += x_gap

    if show_legend:
        _add_legend(svg,
                    hue_order,
                    colors,
                    pos=(x1, 0))
