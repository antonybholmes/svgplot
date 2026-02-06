import collections
from enum import Enum
from optparse import Option
from typing import Any, Optional, Union

import matplotlib
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde, mannwhitneyu

from . import boxplot, core, graph, swarm
from .axis import Axis, auto_axis
from .svgfigure import SVGFigure


class StatsMode(Enum):
    NONE = 1
    CALC = 2
    SHOW = 3


def _add_violin(
    svg: SVGFigure,
    df: pd.DataFrame,
    max_density: float,
    axes: tuple[Axis, Axis],
    color: str = "blue",
    opacity: float = 0.3,
    pos: tuple[int, int] = (0, 0),
    clip: bool = True,
):
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
        p = (
            x - xaxis.scale(df["x"][i] / max_density),
            y + yaxis.w - yaxis.scale(df["y"][i], clip=clip),
        )

        id = f"{p[0]}:{p[1]}"

        if id in used:
            continue

        used.add(id)

        points1.append(p)

    # if points1[0][0] != x:
    #    points1.insert(0, (x, y + yaxis.w))

    # points1[-1][0] = x

    points1 = np.array(points1)

    points2 = []

    for i in range(points1.shape[0] - 1, -1, -1):
        p = (2 * x - points1[i][0], points1[i][1])

        id = f"{p[0]}:{p[1]}"

        if id in used:
            continue

        used.add(id)

        points2.append(p)

    # points2[0][0] = x
    # points2[-1][0] = x

    points2 = np.array(points2)

    points = np.concatenate([points1, points2])

    svg.add_polygon(points, color=color, fill=color, fill_opacity=opacity)


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


def add_violinplot(
    svg: SVGFigure,
    data: pd.DataFrame,
    x: str = "",
    y: str = "",
    hue: Optional[str] = None,
    order: Optional[list[str]] = None,
    hue_order: Optional[list[str]] = None,
    palette: Optional[list[str]] = None,
    scale: str = "area",
    scale_hue: bool = True,
    pos: tuple[int, int] = (0, 0),
    plot_width: int = 80,
    height: int = 500,
    x_gap: int = 20,
    title_offset: int = -50,
    show_legend: bool = False,
    stats_mode: Optional[str] = "show",
    show_labels: bool = False,
    stats_file: Optional[str] = None,
    title: Optional[str] = None,
    bw_kws: Optional[dict[str, Any]] = None,
    x_kws: Optional[dict[str, Any]] = None,
    y_kws: Optional[dict[str, Any]] = None,
    violin_kws: Optional[dict[str, Any]] = None,
    swarm_kws: Optional[dict[str, Any]] = None,
    box_kws: Optional[dict[str, Any]] = None,
) -> None:

    _bw_kws = core.kws({"bw": "scott", "cut": 2, "gridsize": 100}, bw_kws)

    _x_kws = core.kws(
        {
            "show": True,
            "show_labels": True,
            "show_axis": True,
            "label_pos": "axis",
            "label_orientation": "h",
            "labels": None,
        },
        x_kws,
    )
    _y_kws = core.kws(
        {
            "show": True,
            "lim": None,
            "ticks": None,
            "ticklabels": None,
            "offset": None,
            "label": None,
        },
        y_kws,
    )
    _violin_kws = core.kws({"show": True, "opacity": 0.5}, violin_kws)
    _swarm_kws = core.kws(
        {
            "show": False,
            "dot_size": 10,
            "opacity": 0.7,
            "style": swarm.PlotStyle.TRIANGLE,
        },
        swarm_kws,
    )
    _box_kws = core.kws(
        {
            "show": True,
            "width": 20,
            "whisker_width": 20,
            "stroke": 4,
            "dot_size": 12,
            "fill": "white",
            "line_color": None,
            "opacity": 1,
            "rounded": True,
            "median_style": boxplot.MedianStyle.CIRCLE,
        },
        box_kws,
    )

    if palette is None:
        palette = matplotlib.cm.Set2

    if isinstance(palette, matplotlib.colors.ListedColormap):
        palette = [core.rgbtohex(c) for c in palette.colors]

    if isinstance(palette, str):
        p = matplotlib.cm.get_cmap(palette)

    if isinstance(palette, list):
        if isinstance(palette[0], tuple) or isinstance(palette[0], list):
            palette = [core.rgbtohex(c) for c in palette]

        palette = np.array(palette)

    if order is None:
        order = []
        used_hues = set()

        for n in data[x]:
            if n in used_hues:
                continue

            order.append(n)
            used_hues.add(n)

    order = np.array(order)

    # if hue specified but no order given, use order of appearance
    if hue is not None and hue_order is None:
        hue_order = []
        used_hues = set()

        for n in data[hue]:
            if n in used_hues:
                continue

            hue_order.append(n)
            used_hues.add(n)

    # if hue order is still None, just use all
    if hue_order is not None:
        # we only want colors for the hues we have
        palette = palette[0 : len(hue_order)]
    else:
        hue_order = ["<all>"]

    hue_order = np.array(hue_order)

    print(order, hue_order)

    x1, y1 = pos

    if _y_kws["lim"] is None:
        _y_kws["lim"] = (data[y].min(), data[y].max())

    if _y_kws["offset"] is None:
        _y_kws["offset"] = -(plot_width / 2 + x_gap)

    if _y_kws["label"] is None:
        _y_kws["label"] = y

    xaxis = Axis(lim=[0, 1], w=plot_width / 2)
    yaxis = auto_axis(
        _y_kws["lim"],
        label=_y_kws["label"],
        w=height,
    )

    # Axis(
    #     lim=_y_kws["lim"],
    #     ticks=_y_kws["ticks"],
    #     ticklabels=_y_kws["ticklabels"],
    #     label=_y_kws["label"],
    #     w=height,
    # )

    if _y_kws["show"]:
        graph.add_y_axis(svg, axis=yaxis, pos=(_y_kws["offset"], 0))

    densities = collections.defaultdict(lambda: collections.defaultdict(lambda: None))
    data_points = collections.defaultdict(lambda: collections.defaultdict(lambda: None))

    global_max_density = 0
    max_densities = np.zeros(order.size)

    # track which hues are present for each x label
    # used_hues = collections.defaultdict(set)

    for x_labeli, x_label in enumerate(order):
        x_data = data[data[x] == x_label] if x_label != "<all>" else data

        print("x", x_label, x_data, hue_order)

        for hue_label in hue_order:
            # only filter by hue if specified
            if hue_label != "<all>":
                hue_data = x_data[x_data[hue] == hue_label]
            else:
                hue_data = x_data

            # print(x_label, hue_label, hue_data.shape)

            if hue_data.shape[0] == 0:
                continue

            d = hue_data[y]
            data_points[x_label][hue_label] = d

            if hue_data.shape[0] > 1:

                print(x_label, d.values.size, "hue:" + str(hue_label))

                kde, bw_used = _fit_kde(d.values, _bw_kws["bw"])

                x_d = _kde_support(
                    d.values,
                    bw=bw_used,
                    cut=_bw_kws["cut"],
                    gridsize=_bw_kws["gridsize"],
                )

                # print("---")
                # print(type(x_d))
                # print(x_d)
                # print(x_d.dtype)

                density = kde.evaluate(x_d)

                df = pd.DataFrame()
                df["x"] = density
                df["y"] = x_d

                densities[x_label][hue_label] = df

                global_max_density = max(global_max_density, density.max())
                max_densities[x_labeli] = max(max_densities[x_labeli], density.max())
            # else:
            # densities[x_label][hue_label].append(None)

            # used_hues[x_label].add(hue_label)

    # colori = 0
    # w = (hue_order.size - 1) * plot_width
    total_width = 0

    for i, x_label in enumerate(order):
        total_width += len(data_points[x_label]) * plot_width + (x_gap if i > 0 else 0)
    total_width -= plot_width

    if title is not None:
        svg.add_text_bb(
            title,
            x=x1 + total_width / 2,
            y=y1 - 20,
            align="c",
        )

    for x_labeli, x_label in enumerate(order):

        w = len(data_points[x_label]) * plot_width

        label = (
            _x_kws["labels"][x_labeli]
            if isinstance(_x_kws["labels"], list)
            else x_label
        )

        if _x_kws["show_labels"]:
            if _x_kws["label_pos"] == "title":
                svg.add_text_bb(label, x=x1 + w / 2, y=title_offset, align="c")
            else:
                if _x_kws["label_orientation"] == "v":
                    svg.add_text_bb(
                        label,
                        x=x1,
                        y=y1 + yaxis.w + 10,
                        orientation="v",
                        align="r",
                    )
                else:
                    svg.add_text_bb(label, x=x1 + w / 2, y=y1 + yaxis.w + 50, align="c")

        for hi, hue_label in enumerate(hue_order):
            # no data for this hue
            if hue_label not in data_points[x_label]:
                continue

            color = palette[hi % palette.size]

            dp = data_points[x_label][hue_label]

            # can be None if too few data points to fit KDE
            df = densities[x_label][hue_label]

            # determines how violin appears and whether
            # violins are scaled relative to each other

            # if too few data points, skip violin
            if _violin_kws["show"] and df is not None:
                if scale == "area":
                    if scale_hue:
                        md = max_densities[x_labeli]
                    else:
                        md = global_max_density
                else:
                    md = df["x"].max()

                _add_violin(
                    svg,
                    df,
                    md,
                    axes=(xaxis, yaxis),
                    color=color,
                    opacity=_violin_kws["opacity"],
                    pos=(x1, y1),
                )

            # iqr line

            if _swarm_kws["show"]:
                swarm._add_swarm(
                    svg,
                    dp,
                    axes=(xaxis, yaxis),
                    dot_size=_swarm_kws["dot_size"],
                    color=color,
                    opacity=_swarm_kws["opacity"],
                    pos=(x1, y1),
                    style=_swarm_kws["style"],
                )

            if _box_kws["show"]:
                boxplot._add_boxplot(
                    svg,
                    dp,
                    axes=(xaxis, yaxis),
                    width=_box_kws["width"],
                    whisker_width=_box_kws["whisker_width"],
                    color=color,
                    line_color=_box_kws["line_color"],
                    median_style=_box_kws["median_style"],
                    dot_size=_box_kws["dot_size"],
                    fill=_box_kws["fill"],
                    opacity=_box_kws["opacity"],
                    stroke=_box_kws["stroke"],
                    pos=(x1, y1),
                    rounded=_box_kws["rounded"],
                    label=hue_label if show_labels else None,
                )

            x1 += plot_width  # 2 * xaxis.w
            # colori += 1

        x1 += x_gap

    if _x_kws["show_axis"]:
        svg.add_line(
            x1=pos[0] - plot_width / 2 - x_gap,
            x2=x1 - plot_width / 2 - x_gap,
            y1=y1 + yaxis.w,
        )

    if show_legend:
        swarm._add_legend(svg, hue_order, palette, pos=(x1 - plot_width + 40, 0))

    #
    # Stats
    #

    test_pairs = [(x, y) for x in order for y in hue_order]

    print("test pairs:", test_pairs)

    df_stats = None

    if stats_mode != "none":
        d = np.ones((len(test_pairs), len(test_pairs)))  # bonferroni correction

        print(d.size)
        stats = []
        n = len(test_pairs) * len(test_pairs)

        for p1, (xc1, hue1) in enumerate(test_pairs):

            d1 = (
                data[(data[x] == xc1) & (data[hue] == hue1)]
                if hue1 != "<all>"
                else data[data[x] == xc1]
            )

            for p2, (xc2, hue2) in enumerate(test_pairs):
                if xc1 == xc2 and hue1 == hue2:
                    continue

                d2 = (
                    data[(data[x] == xc2) & (data[hue] == hue2)]
                    if hue2 != "<all>"
                    else data[data[x] == xc2]
                )

                s, p = mannwhitneyu(
                    d1[y],
                    d2[y],
                    alternative="two-sided",
                )

                # print(p)
                # bonferroni
                q = min(1, p * n)
                d[p1, p2] = q
                stats.append([f"{xc1}|{hue1}", f"{xc2}|{hue2}", p, q])

        # for s1, xc1 in enumerate(order):
        #     for s2, xc2 in enumerate(order):
        #         if xc1 == xc2:
        #             continue

        #         for h1, hue1 in enumerate(hue_order):
        #             for h2, hue2 in enumerate(hue_order):
        #                 if hue1 == hue2:
        #                     continue

        #                 s, p = mannwhitneyu(
        #                     data[data[x] == xc1][y], data[data[x] == xc2][y]
        #                 )
        #                 # print(p)
        #                 # bonferroni
        #                 q = min(1, p * d.size)
        #                 d[s1, s2] = q
        #                 stats.append([xc1, xc2, p, q])

        df_stats = pd.DataFrame(stats, columns=[f"{x} 1", f"{x} 2", "p", "q"])

        if stats_file is not None:
            df_stats.to_csv(stats_file, sep="\t", header=True, index=False)

        # dfp = pd.DataFrame(d, index=hue_order, columns=hue_order)
        # dfp.to_csv('bcca_nrc31_subtype_q.tsv', sep='\t', header=True, index=True)

        if stats_mode == "show":
            # count number of lines required
            bars = 0

            for p1, (xc1, hue1) in enumerate(test_pairs):
                for p2, (xc2, hue2) in enumerate(test_pairs):
                    if xc1 == xc2 and hue1 == hue2:
                        continue

                    df_stats_t = df_stats[
                        (df_stats[f"{x} 1"] == f"{xc1}|{hue1}")
                        & (df_stats[f"{x} 2"] == f"{xc2}|{hue2}")
                    ]

                    q = df_stats_t["q"].values[0]

                    if q < 0.05:
                        bars += 1

            # for t1i, t1 in enumerate(order):
            #     for t2i, t2 in enumerate(order):
            #         if t2i > t1i:
            #             df_stats_t = df_stats[
            #                 (df_stats[f"{x} 1"] == t1) & (df_stats[f"{x} 2"] == t2)
            #             ]
            #             if df_stats_t.shape[0] == 0:
            #                 continue

            #             q = df_stats_t["q"].values[0]

            #             if q < 0.05:
            #                 bars += 1

            ty = -bars * 40 - (20 if title is not None else 0)
            # plot_total_width = plot_width + x_gap

            for p1, (xc1, hue1) in enumerate(test_pairs):
                block1 = p1 // hue_order.size
                blockx1 = block1 * (plot_width * hue_order.size + x_gap)
                withinx1 = (p1 % hue_order.size) * plot_width
                x1 = blockx1 + withinx1
                for p2, (xc2, hue2) in enumerate(test_pairs):
                    if xc1 == xc2 and hue1 == hue2:
                        continue

                    block2 = p2 // hue_order.size
                    blockx2 = block2 * (plot_width * hue_order.size + x_gap)
                    withinx2 = (p2 % hue_order.size) * plot_width
                    x2 = blockx2 + withinx2

                    df_stats_t = df_stats[
                        (df_stats[f"{x} 1"] == f"{xc1}|{hue1}")
                        & (df_stats[f"{x} 2"] == f"{xc2}|{hue2}")
                    ]

                    q = df_stats_t["q"].values[0]

                    if q < 0.05:
                        if q < 0.001:
                            stars = "***"
                        elif q < 0.01:
                            stars = "**"
                        else:
                            stars = "*"

                        if (
                            xc1 == "Kostia"
                            and hue1 == "GCB"
                            and xc2 == "BCCA"
                            and hue2 == "ABC"
                        ):
                            print("here", x1, x2, p1, p2, block1, block2)

                        svg.add_text_bb(
                            stars,  # + f"{xc1}|{hue1}" + f"{xc2}|{hue2}",
                            x=(x1 + x2) / 2,
                            y=ty,
                            align="c",
                        )
                        svg.add_line(x1, ty, x2, ty)
                        svg.add_line(
                            x1,
                            ty,
                            x1,
                            ty + 10,
                        )
                        svg.add_line(
                            x2,
                            ty,
                            x2,
                            ty + 10,
                        )
                        ty += 40

            # for t1i, t1 in enumerate(order):
            #     for t2i, t2 in enumerate(order):
            #         if t2i > t1i:
            #             df_stats_t = df_stats[
            #                 (df_stats[f"{x} 1"] == t1) & (df_stats[f"{x} 2"] == t2)
            #             ]
            #             if df_stats_t.shape[0] == 0:
            #                 continue

            #             q = df_stats_t["q"].values[0]

            #             if q < 0.05:
            #                 if q < 0.001:
            #                     stars = "***"
            #                 elif q < 0.01:
            #                     stars = "**"
            #                 else:
            #                     stars = "*"

            #                 svg.add_text_bb(
            #                     stars,
            #                     x=(t1i + t2i) * plot_total_width / 2,
            #                     y=ty,
            #                     align="c",
            #                 )
            #                 svg.add_line(
            #                     t1i * plot_total_width, ty, t2i * plot_total_width, ty
            #                 )
            #                 svg.add_line(
            #                     t1i * plot_total_width,
            #                     ty,
            #                     t1i * plot_total_width,
            #                     ty + 10,
            #                 )
            #                 svg.add_line(
            #                     t2i * plot_total_width,
            #                     ty,
            #                     t2i * plot_total_width,
            #                     ty + 10,
            #                 )
            #                 ty += 40

    return {"w": x1 - x_gap - plot_width, "h": height, "stats": df_stats}
