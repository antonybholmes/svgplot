import math
from enum import Enum
from typing import Any, Mapping, Optional, Union

import matplotlib
import numpy as np
import pandas as pd
import seaborn as sns

from . import core, graph
from . import hatch as phatch
from . import svgfiguredraw
from .axis import Axis
from .svgfigure import SVGFigure


def add_barplot(
    svg: SVGFigure,
    data: pd.DataFrame,
    x: str = "x",
    y: str = "y",
    hue: Optional[str] = None,
    x_order: Optional[list[str]] = None,
    hue_order: Optional[list[str]] = None,
    x_palette: dict[str, str] = {},
    hue_palette: dict[str, str] = {},
    pos: tuple[int, int] = (0, 0),
    bar_labels: Optional[str] = None,
    bar_label_offset: int = 20,
    height=400,
    bar_width=60,
    x_gap: int = 10,
    hue_gap: int = 0,
    bar_color="#cccccc",
    ylim=[0, 100],
    yticks=[0, 50, 100],
    show_yaxis=True,
    show_xlabels: bool = True,
    ylabel: Optional[str] = None,  #'% cells',
    xlabel_orientation: str = "v",
    rename: dict[str, str] = {},
):

    xp, yp = pos

    yaxis = Axis(lim=ylim, w=height)

    # w = means.size * block_size

    # xaxis = axis.Axis(lim=[0, df.shape[1]], w=w)

    y_base_line = yp + height

    if ylabel is None:
        ylabel = y

    if x is None:
        x = ""

    if y is None:
        y = ""

    if x_order is None:
        if x != "":
            x_order = sorted(data[x].unique())
        else:
            x_order = [""]

    x_order = np.array(x_order)

    if hue is None:
        hue = ""

    if hue_order is None:
        hue_order = [""]  # sorted(data[hue].unique())

    hue_order = np.array(hue_order)

    # draw bars

    x1 = xp

    for xo in x_order:
        # print("xo", xo)

        # the data for the x group
        if x != "":
            dfx = data[data[x] == xo]
        else:
            dfx = data

        color = bar_color
        hatch = "solid"

        # first determine color based on the x palette
        if xo in x_palette:
            p = x_palette[xo]
            if ":" in p:
                color, hatch = p.split(":")[0:2]
            else:
                color = p

        w = len(hue_order) * bar_width + (len(hue_order) - 1) * hue_gap

        if show_xlabels:
            label = rename.get(xo, xo)

            if xlabel_orientation == "v":
                svg.add_text_bb(
                    label,
                    x=x1 + w / 2,
                    y=y_base_line + 20,
                    orientation="v",
                    align="r",
                )
            else:
                svg.add_text_bb(
                    label,
                    x=x1 + w / 2,
                    y=y_base_line + 30,
                    align="c",
                )

        # iterate through x group using the hue
        for ho in hue_order:
            if ho != "":
                dfh = dfx[dfx[hue] == ho]
            else:
                dfh = dfx

            if y != "":
                yd = dfh[y].values
            else:
                yd = dfh.iloc[:, 0].values

            label = ""

            if bar_labels is not None:
                # use the first value as the label
                label = dfh[bar_labels].values[0]

            mean = yd.mean()
            h = yaxis.scale(mean)

            # use the hue palette to override
            # any previously defined color
            if ho in hue_palette:
                p = hue_palette[ho]

                if ":" in p:
                    c1, hatch = p.split(":")[0:2]
                else:
                    c1 = p

                if c1 != "":
                    color = c1

            y1 = y_base_line - h

            phatch.add_hatch(svg, x1, y1, bar_width, h, hatch=hatch, color=color)

            svg.add_rect(x1, y1, bar_width, h, color="black")

            if label != "":
                svg.add_text_bb(
                    label, x=x1 + bar_width / 2, align="c", y=y1 - bar_label_offset
                )

            x1 += bar_width + hue_gap

        x1 += x_gap

    if show_yaxis:
        graph.add_y_axis(
            svg, axis=yaxis, pos=(xp - x_gap, yp), ticks=yticks, label=ylabel
        )

    return {"w": x1 - x_gap, "h": height}


def add_v_barplot(
    svg: SVGFigure,
    data: pd.DataFrame,
    x: str = "x",
    y: str = "y",
    hue: Optional[str] = None,
    order: Optional[list[str]] = None,
    hue_order: Optional[list[str]] = None,
    x_palette: dict[str, str] = {},
    palette: dict[str, str] = {},
    pos: tuple[int, int] = (0, 0),
    width=300,
    bar_width=60,
    x_gap: int = 10,
    hue_gap: int = 0,
    bar_color="#cccccc",
    xlim=[0, 100],
    xticks=[0, 50, 100],
    ticklabels: Optional[list[str]] = None,
    show_xaxis=True,
    xlabel="% cells",
    rename: dict[str, str] = {},
    invert: bool = False,
    showlabels: bool = True,
    overlay: bool = False,
):
    xp, yp = pos

    xaxis = Axis(lim=xlim, w=width, invert=invert)

    # w = means.size * block_size

    # xaxis = axis.Axis(lim=[0, df.shape[1]], w=w)

    if ticklabels is None:
        ticklabels = xticks

    x2 = xp + width

    if order is None:
        order = data[x].values

    order = np.array(order)

    if hue is None:
        hue = ""

    if hue_order is None:
        hue_order = [""]  # sorted(data[hue].unique())

    hue_order = np.array(hue_order)

    # draw bars

    data = data.iloc[np.where(~np.isnan(data[y]))]

    y3 = yp

    for xo in order:
        print("xo", xo)

        if x != "":
            dfx = data[data[x] == xo]
        else:
            dfx = data

        color = bar_color
        hatch = "solid"

        if xo in x_palette:
            p = x_palette[xo]
            if ":" in p:
                color, hatch = p.split(":")[0:2]
            else:
                color = p

        w = len(hue_order) * bar_width + (len(hue_order) - 1) * hue_gap

        if showlabels:
            svg.add_text_bb(rename.get(xo, xo), x=-20, y=y3 + w / 2, align="r")

        for ho in hue_order:
            if ho != "":
                dfh = dfx[dfx[hue] == ho]
            else:
                dfh = dfx

            if y != "":
                yd = dfh[y].values
            else:
                yd = dfh.iloc[:, 0].values

            print("d", yd)
            mean = yd.mean()
            sd = yd.std()

            if math.isnan(mean):
                mean = 0
                sd = 0

            h = xaxis.scale(mean)
            sdh = xaxis.scale(sd)

            h1 = h - sdh
            h2 = h + sdh

            if ho in palette:
                print(ho, palette)
                p = palette[ho]

                if ":" in p:
                    c1, hatch = p.split(":")[0:2]
                else:
                    c1 = p

                if c1 != "":
                    color = c1

            if invert:
                w = xaxis.w - h
                print(h, w, mean, "wath")

                phatch.add_hatch(svg, h, y3, w, bar_width, hatch=hatch, color=color)

                svg.add_rect(h, y3, w, bar_width, color="black")
            else:
                phatch.add_hatch(svg, 0, y3, h, bar_width, hatch=hatch, color=color)

                svg.add_rect(0, y3, h, bar_width, color="black")

            if not overlay:
                y3 += bar_width + hue_gap

        y3 += x_gap

        if overlay:
            y3 += bar_width

    if show_xaxis:
        graph.add_x_axis(
            svg,
            axis=xaxis,
            pos=(xp, y3),
            ticks=xticks,
            ticklabels=ticklabels,
            label=xlabel,
        )

    return {"width": width, "height": y3 - x_gap}


def add_stacked_bar(
    svg: SVGFigure,
    df,
    x: str,
    y: str,
    hue: str,
    x_order: Optional[list[str]] = None,
    hue_order: Optional[list[str]] = None,
    palette: Union[list, dict, matplotlib.colors.ListedColormap] = None,
    pos=(0, 0),
    height=400,
    bar_width=60,
    bar_padding=10,
    bar_color="#cccccc",
    ylim=[0, 100],
    yticks=None,
    xlabel="",
    ylabel="% cells",
    padding=10,
    showborder=True,
    as_pc=True,
    legend: bool = True,
    invert: bool = False,
    showlabels: bool = True,
    labelpos: str = "bottom",
):
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
        palette = {
            hue_order[i]: palette[i % len(palette)] for i in range(len(hue_order))
        }

    if yticks is None:
        yticks = range(0, 120, 20)

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

        yaxis = Axis(lim=[0, 100], ticks=yticks, w=height)
    else:
        # pc_tables = tables
        yaxis = Axis(lim=ylim, w=height)

    block_size = bar_width + 2 * bar_padding

    # w = means.size * block_size

    # xaxis = axis.Axis(lim=[0, df.shape[1]], w=w)

    y2 = y1 + (0 if invert else height)

    # draw bars

    x2 = x1 + bar_padding

    if x_order is None:
        x_order = []

        for c in df[x]:
            if c not in x_order:
                x_order.append(c)

    for c in x_order:
        dfc = df[df[x] == c]
        y3 = y2

        for hi, h in enumerate(hue_order):
            dfh = dfc[dfc[hue] == h]

            print(dfc)
            print(h, dfh)

            h1 = yaxis.scale(dfh[y].values[0])
            y4 = y3 - h1

            if h in palette:
                bar_color = palette[h]
            else:
                bar_color = "gray"

            # print("fg:", x2)
            # print("ert:", bar_width)
            # print("fg2:", h1, bar_color)

            bar_y = y3 if invert else y4

            svg.add_rect(x2, bar_y, bar_width, h1, fill=bar_color)

            if showborder:
                svg.add_rect(x2, bar_y, bar_width, h1, color="black")

            if invert:
                y3 += h1
            else:
                y3 -= h1

        if showlabels:
            if labelpos == "top":
                svg.add_text_bb(
                    c, x=x2 + bar_width / 2, y=y1 - 20, align="l", orientation="v"
                )
            else:
                # bottom
                svg.add_text_bb(
                    c, x=x2 + bar_width / 2, y=y2 + 20, align="r", orientation="v"
                )

        x2 += block_size

    svg.add_line(x2=x2, y1=y2)

    ticklabels = yaxis.ticks

    if invert:
        # reverse
        ticklabels = ticklabels[::-1]

    graph.add_y_axis(
        svg,
        axis=yaxis,
        pos=pos,
        ticks=yticks,
        ticklabels=ticklabels,
        label=ylabel,
        title_offset=100,
    )

    # svg.inc(x=x2 + 50)

    if legend:
        for hi, h in enumerate(hue_order):
            svg.add_bullet(
                h, shape="s", color=palette[h], text_color="black", x=x2 + 50, y=hi * 50
            )


def add_v_stacked_bar(
    svg: SVGFigure,
    df,
    x: str,
    y: str,
    hue: str,
    x_order: Optional[list[str]] = None,
    hue_order: Optional[list[str]] = None,
    palette: Union[list, dict, matplotlib.colors.ListedColormap] = None,
    pos=(0, 0),
    height=400,
    bar_width=60,
    bar_padding=10,
    bar_color="#cccccc",
    ylim=[0, 100],
    yticks=None,
    xlabel="",
    ylabel="% cells",
    padding=10,
    showborder=True,
    as_pc=True,
    legend: bool = True,
    invert: bool = False,
    showlabels: bool = True,
    labelpos: str = "left",
):
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
        palette = {
            hue_order[i]: palette[i % len(palette)] for i in range(len(hue_order))
        }

    if yticks is None:
        yticks = range(0, 120, 20)

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

        yaxis = Axis(lim=ylim, ticks=yticks, w=height, invert=invert)
    else:
        # pc_tables = tables
        yaxis = Axis(lim=ylim, w=height, invert=invert)

    block_size = bar_width + 2 * bar_padding

    # w = means.size * block_size

    # xaxis = axis.Axis(lim=[0, df.shape[1]], w=w)

    y2 = y1 + (0 if invert else height)

    # draw bars

    x2 = x1 + bar_padding

    if x_order is None:
        x_order = []

        for c in df[x]:
            if c not in x_order:
                x_order.append(c)

    for c in x_order:
        dfc = df[df[x] == c]
        y3 = y2

        for hi, h in enumerate(hue_order):
            dfh = dfc[dfc[hue] == h]

            print("huh", c, h)

            h1 = yaxis.scale(dfh[y].values[0]) if dfh.shape[0] > 0 else 0
            y4 = y3 - h1

            if h in palette:
                bar_color = palette[h]
            else:
                bar_color = "gray"

            # print("fg:", x2)
            # print("ert:", bar_width)
            # print("fg2:", h1, bar_color)

            bar_y = y3 if invert else y4

            svg.add_rect(bar_y, x2, h1, bar_width, fill=bar_color)

            if showborder:
                svg.add_rect(bar_y, x2, h1, bar_width, color="black")

            if invert:
                y3 += h1
            else:
                y3 -= h1

        if showlabels:
            if labelpos == "left":
                svg.add_text_bb(c, y=x2 + bar_width / 2, x=y1 - 20, align="r")
            else:
                # bottom
                svg.add_text_bb(c, y=x2 + bar_width / 2, x=y2 + 20, align="l")

        x2 += block_size

    svg.add_line(y2=x2, x1=y2)

    ticklabels = yaxis.ticks

    if invert:
        # reverse
        ticklabels = ticklabels[::-1]

    graph.add_x_axis(
        svg,
        axis=yaxis,
        pos=pos,
        ticks=yticks,
        ticklabels=ticklabels,
        label=ylabel,
        title_offset=100,
    )

    # svg.inc(x=x2 + 50)

    if legend:
        for hi, h in enumerate(hue_order):
            svg.add_bullet(
                h, shape="s", color=palette[h], text_color="black", x=x2 + 50, y=hi * 50
            )
