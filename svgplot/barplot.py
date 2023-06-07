from typing import Mapping, Optional, Union, Any

import matplotlib
from .axis import Axis
from .svgfigure import SVGFigure
from . import svgfiguredraw
import numpy as np
import math
from . import graph
from . import hatch as phatch
from enum import Enum
import pandas as pd
from . import core
import seaborn as sns


def add_barplot(svg: SVGFigure,
                data: pd.DataFrame,
                x: str = 'x',
                y: str = 'y',
                hue: Optional[str] = None,
                order: Optional[list[str]] = None,
                hue_order: Optional[list[str]] = None,
                x_palette: dict[str, str] = {},
                palette: dict[str, str] = {},
                pos: tuple[int, int] = (0, 0),
                height=400,
                bar_width=60,
                x_gap: int = 10,
                hue_gap: int = 0,
                bar_color='#cccccc',
                ylim=[0, 100],
                yticks=[0, 50, 100],
                xlabel='',
                ylabel='% cells',
                rename: dict[str, str] = {}):

    xp, yp = pos

    yaxis = Axis(lim=ylim, w=height)

    # w = means.size * block_size

    # xaxis = axis.Axis(lim=[0, df.shape[1]], w=w)

    y2 = yp + height

    if x is None:
        x = ''

    if y is None:
        y = ''

    if order is None:
        if x != '':
            order = sorted(data[x].unique())
        else:
            order = ['']

    order = np.array(order)

    if hue is None:
        hue = ''

    if hue_order is None:
        hue_order = ['']  # sorted(data[hue].unique())

    hue_order = np.array(hue_order)

    # draw bars

    x1 = xp

    for xo in order:
        print('xo', xo)

        if x != '':
            dfx = data[data[x] == xo]
        else:
            dfx = data

        color = bar_color
        hatch = 'solid'

        if xo in x_palette:
            p = x_palette[xo]
            if ':' in p:
                color, hatch = p.split(':')[0:2]
            else:
                color = p

        w = len(hue_order) * bar_width + (len(hue_order) - 1) * hue_gap

        svg.add_text_bb(rename.get(xo, xo), x=x1+w/2,
                        y=y2, orientation='v', align='r')

        for ho in hue_order:
            if ho != '':
                dfh = dfx[dfx[hue] == ho]
            else:
                dfh = dfx

            if y != '':
                yd = dfh[y].values
            else:
                yd = dfh.iloc[:, 0].values

            mean = yd.mean()
            sd = yd.std()

            h = yaxis.scale(mean)
            sdh = yaxis.scale(sd)
            h1 = h - sdh
            h2 = h + sdh

            if ho in palette:
                p = palette[ho]

                if ':' in p:
                    c1, hatch = p.split(':')[0:2]
                else:
                    c1 = p

                if c1 != '':
                    color = c1

            y1 = y2 - h

            phatch.add_hatch(svg, x1, y1, bar_width, h,
                             hatch=hatch, color=color)

            svg.add_rect(x1, y1, bar_width, h, color='black')

            x1 += bar_width + hue_gap

        x1 += x_gap

    graph.add_y_axis(svg, axis=yaxis, pos=(
        xp - x_gap, yp), ticks=yticks, label=ylabel)


def add_stacked_bar(svg: SVGFigure,
                    df,
                    x: str,
                    y: str,
                    hue: str,
                    hue_order=None,
                    palette: Union[list, dict,
                                   matplotlib.colors.ListedColormap] = None,
                    pos=(0, 0),
                    height=400,
                    bar_width=60,
                    bar_padding=10,
                    bar_color='#cccccc',
                    ylim=[0, 100],
                    yticks=None,
                    xlabel='',
                    ylabel='% cells',
                    padding=10,
                    showborder=True,
                    as_pc=True):
    # self.set_font_size(svgplot.FIGURE_FONT_SIZE)

    x1, y1 = pos

    if hue_order is None:
        hue_order = np.array(sorted(df[hue].unique()))

    if palette is None:
        palette = sns.color_palette("hls", len(hue_order))

    if isinstance(palette, matplotlib.colors.ListedColormap):
        palette = [core.rgbtohex(c) for c in palette.colors]

    if isinstance(palette, list):
        if isinstance(palette[0], tuple) or isinstance(palette[0], list):
            palette = [core.rgbtohex(c) for c in palette]

    if isinstance(palette, list):
        palette = {hue_order[i]: palette[i %
                                         len(palette)] for i in range(len(hue_order))}

    if as_pc:
        tables = []
        for c in df[x].unique():
            dfc = df[df[x] == c]
            s = np.sum(dfc[y].values)
            if s > 0:
                dfc[y] = dfc[y] / s * 100
            tables.append(dfc)

        df = pd.concat(tables, axis=0)

        # pc_tables = [(t / t.sum(axis=0) * 100) for t in tables]

        yaxis = Axis(lim=[0, 100], ticks=range(0, 120, 20), w=height)
    else:
        # pc_tables = tables
        yaxis = Axis(lim=ylim, w=height)

    block_size = bar_width + 2 * bar_padding

    # w = means.size * block_size

    # xaxis = axis.Axis(lim=[0, df.shape[1]], w=w)

    y2 = y1 + height

    # draw bars

    x2 = x1 + bar_padding

    groups = []

    for c in df[x]:
        if c not in groups:
            groups.append(c)

    for c in groups:
        dfc = df[df[x] == c]
        y3 = y2

        for hi, h in enumerate(hue_order):
            dfh = dfc[dfc[hue] == h]

            print(dfc)
            print(h, dfh)

            print('qwe', dfh[y].values[0])

            h1 = yaxis.scale(dfh[y].values[0])
            y4 = y3 - h1

            if h in palette:
                bar_color = palette[h]
            else:
                bar_color = 'gray'

            print('fg:', x2)
            print('ert:', bar_width)
            print('fg2:', h1, bar_color)
            svg.add_rect(x2, y4, bar_width, h1, fill=bar_color)
            
            if showborder:
                svg.add_rect(x2, y4, bar_width, h1, color='black')
            
            y3 -= h1

        svg.add_text_bb(c, x=x2+bar_width/2, y=y2+20, align='r', orientation='v')

        x2 += block_size

    svg.add_line(x2=x2, y1=y2)

    graph.add_y_axis(svg, axis=yaxis, pos=pos, ticks=yticks, label=ylabel, title_offset=100)

    svg.inc(x=x2 + 50)

    for h in hue_order:
        svg.add_bullet(h, shape='s', color=palette[h], text_color='black')
        svg.inc(y=50)
