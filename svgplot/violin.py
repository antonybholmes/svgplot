from optparse import Option
from typing import Any, Optional, Union
from scipy.stats import gaussian_kde
from pandas import DataFrame
from .svgfigure import SVGFigure
import matplotlib
import numpy as np
from . import svgplot
from .axis import Axis
from . import graph
from . import swarm
from . import boxplot




def _add_violin(svg: SVGFigure,
                df: DataFrame,
                max_density: float,
                axes: tuple[Axis, Axis],
                color: str = 'blue',
                opacity: float = 0.3,
                pos: tuple[int, int] = (0, 0),
                clip: bool = True):
    """Add the base violin to a plot

    Args:
        svg (SVGFigure): SVG canvas to draw on.
        df (DataFrame): Data to render.
        max_density (float): Controls the height of the KDE
        axes (tuple[Axis, Axis]): x and y axes.
        color (str, optional): Color of violin. Defaults to 'blue'.
        opacity (float, optional): Opacity between 0 and 1 to govern translucency. Defaults to 0.3.
        pos (tuple[int, int], optional): Initial relative offset position to render from. Defaults to (0, 0).
        clip (bool, optional): Whether to clip coordinates so the plot does not exceed the y lim. Defaults to True.
    """
    x, y = pos

    xaxis, yaxis = axes

    used = set()

    points1 = []

    for i in range(0, df.shape[0]):
        p = (x - xaxis.scale(df['x'][i]/max_density), y + yaxis.w - yaxis.scale(df['y'][i], clip=clip))

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
                   palette: Optional[list[str]] = None,
                   scale: str = 'area',
                   scale_hue: bool = True,
                   plot_width: int = 80,
                   height: int = 500,
                   x_gap: int = 20,
                   title_offset: int = -50,
                   show_legend: bool = False,
                   pos: tuple[int, int] = (0, 0),
                   bw_kws: Optional[dict[str, Any]] = None,
                   x_kws: Optional[dict[str, Any]] = None,
                   y_kws: Optional[dict[str, Any]] = None,
                   violin_kws: Optional[dict[str, Any]] = None,
                   swarm_kws: Optional[dict[str, Any]] = None,
                   box_kws: Optional[dict[str, Any]] = None) -> None:

    _bw_kws = svgplot.kws({'bw': 'scott', 'cut': 2, 'gridsize': 100}, bw_kws)

    _x_kws = svgplot.kws({'show': True, 'show_labels': True, 'show_axis':True, 'label_pos':'axis', 'label_orientation': 'h'}, x_kws)
    _y_kws = svgplot.kws({'show': True, 'lim': None, 'ticks': None,
                  'ticklabels': None, 'offset': None, 'title': None}, y_kws)
    _violin_kws = svgplot.kws({'show': True, 'opacity': 0.3}, violin_kws)
    _swarm_kws = svgplot.kws({'show': True, 'dot_size': 10, 'opacity': 0.7, 'style': '^'}, swarm_kws)
    _box_kws = svgplot.kws({'show': True, 'width': 20, 'whisker_width': 20, 'stroke': 3, 'dot_size': 12,
                    'fill': 'white', 'opacity': 1, 'rounded': True, 'median_style': 'circle'}, box_kws)

    if palette is None:
        palette = matplotlib.cm.Set2

    if isinstance(palette, matplotlib.colors.ListedColormap):
        palette = [svgplot.rgbtohex(c) for c in palette.colors]

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
                 ticklabels=_y_kws['ticklabels'], label=y_kws['title'], w=height)

    densities = []
    data_points = []

    global_max_density = 0
    max_densities = np.zeros(x_order.size)

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
            max_densities[labeli] = max(max_densities[labeli], density.max())

    colori = 0

    for labeli, label in enumerate(x_order):
        w = (hue_order.size - 1) * plot_width

        if _x_kws['show_labels']:
            match _x_kws['label_pos']:
                case 'title':
                    svg.add_text_bb(label, x=x1+w/2, y=title_offset, align='c')
                case _:
                    if _x_kws['label_orientation'] == 'v':
                        svg.add_text_bb(label, x=x1+w/2, y=y1+yaxis.w+10, orientation='v', align='r')
                    else:
                        svg.add_text_bb(label, x=x1+w/2, y=y1+yaxis.w+50, align='c')

        for huei, hue_label in enumerate(hue_order):
            color = palette[colori % palette.size]

            dp = data_points[colori]

            df = densities[colori]

            match scale:
                case 'area':
                    if scale_hue:
                        md = max_densities[labeli]
                    else:
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
                swarm.add_swarm(svg,
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

            x1 += plot_width #2 * xaxis.w
            colori += 1

        

        x1 += x_gap

    if _x_kws['show_axis']:
        print(x, x1, y1+yaxis.w)
        svg.add_line(x1=pos[0]-plot_width/2-x_gap, x2=x1-plot_width/2-x_gap, y1=y1+yaxis.w)


    if show_legend:
        _add_legend(svg,
                    hue_order,
                    palette,
                    pos=(x1, 0))

    return (x1, height)
