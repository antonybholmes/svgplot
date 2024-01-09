import json
import math
from typing import Mapping, Union

import pandas as pd
from lifelines import KaplanMeierFitter
from matplotlib import cm

from . import graph
from .axis import Axis
from .svgfigure import SVGFigure
from .svgfiguremod import SVGFigureModule


def _get_censor_kws(
    kws: Mapping[str, Union[int, float, bool, str]]
) -> dict[str, Union[int, float, bool, str]]:
    if kws is None:
        kws = {}

    ret = {"show": True, "shape": "x", "size": 8}
    ret.update(kws)
    return ret


def add_kmf_plot(
    svg: SVGFigure,
    name: str,
    durations: list[float],
    event_observed: list[Union[int, float, bool]],
    axes: tuple[Axis, Axis],
    show_axes: bool = True,
    color: str = "blue",
    pos: tuple[float, float] = (0, 0),
    type: str = "OS",
    censor_kws: Mapping[str, Union[int, float, bool, str]] = None,
    ci_kws: Mapping[str, Union[int, float, bool, str]] = None,
    stroke=5,
) -> None:
    print(name)
    x, y = pos

    _censor_kws = _get_censor_kws(censor_kws)

    if censor_kws is None:
        censor_kws = {}

    if ci_kws is None:
        ci_kws = {}

    _ci_kws = {"show": True, "fill_opacity": 0.2}
    _ci_kws.update(ci_kws)

    xaxis, yaxis = axes
    h = yaxis.w

    kmf = KaplanMeierFitter()
    kmf.fit(durations, event_observed, label=name)

    data = [
        [x, y, censor, cil, cih]
        for x, y, censor, cil, cih in zip(
            kmf.cumulative_density_.index,
            kmf.cumulative_density_.iloc[:, 0],
            kmf.event_table["censored"],
            kmf.confidence_interval_.iloc[:, 0],
            kmf.confidence_interval_.iloc[:, 1],
        )
    ]

    df = pd.DataFrame(data, columns=["x", "y", "censored", "ci_low", "ci_high"])

    df["y"] = (1 - df["y"]) * 100
    df["ci_low"] = df["ci_low"] * 100
    df["ci_high"] = df["ci_high"] * 100

    if _ci_kws["show"]:
        points = [[df["x"].values[0], df["ci_high"].values[0]]]

        for i2 in range(1, df.shape[0]):
            x1, y1 = points[-1]
            x2, y2, censored2, ci_low2, ci_high2 = df.iloc[i2, :].values

            # need to modify x to ensure only right angles
            if y1 != ci_high2:
                points.append([x2, y1])

            points.append([x2, ci_high2])

        points.append([df["x"].values[-1], df["ci_low"].values[-1]])

        for i2 in range(df.shape[0] - 2, -1, -1):
            x1, y1 = points[-1]
            x2, y2, censored2, ci_low2, ci_high2 = df.iloc[i2, :].values

            if y1 != ci_low2:
                points.append([x2, y1])

            points.append([x2, ci_low2])

        # so they are on axes scales
        points = [
            [x + xaxis.scale(x1), y + yaxis.w - yaxis.scale(y1)] for x1, y1 in points
        ]

        svg.add_polygon(points, fill=color, fill_opacity=_ci_kws["fill_opacity"])

    # d = [df.iloc[0, :].values]
    points = [[df["x"].values[0], df["y"].values[0]]]

    for i2 in range(1, df.shape[0]):
        x1, y1 = points[-1]
        x2, y2, censored2, ci_low2, ci_high2 = df.iloc[i2, :].values

        # d.append(df.iloc[i1, :].values)

        # print(x1, y1, x2, y2)

        if y1 != y2:
            # to prevent lines at angles other than 90
            # insert an extra point with the same x as
            # the current spot, but the y of the previous
            # spot
            # d.append([x2, y1, 0, ci_low1, ci_high1])
            # print('add', x1, y1)
            points.append([x2, y1])

        # d.append([x2, y2, censored2, ci_low2, ci_high2])
        points.append([x2, y2])

    # df1 = pd.DataFrame(
    #    d, columns=['x', 'y', 'censored', 'ci_low', 'ci_high'])

    points = [[x + xaxis.scale(x1), y + yaxis.w - yaxis.scale(y1)] for x1, y1 in points]

    svg.add_polyline(points, color=color, stroke=stroke)

    # svg.add_lineplot_v2(df1,
    #                     color=color,
    #                     axes=[xaxis, yaxis],
    #                     xaxis_kws={'show': False},
    #                     yaxis_kws={'show': False},
    #                     stroke=stroke)

    if _censor_kws["show"]:
        # show censors as a cross
        dfc = df[df["censored"] > 0]

        for i in range(0, dfc.shape[0]):
            x1 = xaxis.scale(dfc["x"].values[i])
            y1 = y + h - yaxis.scale(dfc["y"].values[i])
            s = _censor_kws["size"]
            if _censor_kws["shape"] == "x":
                l = math.sin(math.pi / 2) * s
                svg.add_line(
                    x1=x1 - l,
                    y1=y1 - l,
                    x2=x1 + l,
                    y2=y1 + l,
                    color=color,
                    stroke=stroke,
                )
                svg.add_line(
                    x1=x1 - l,
                    y1=y1 + l,
                    x2=x1 + l,
                    y2=y1 - l,
                    color=color,
                    stroke=stroke,
                )
            elif _censor_kws["shape"] == "|":
                # default to crossgraph
                svg.add_line(x1=x1, y1=y1, x2=x1, y2=y1 - s, color=color, stroke=stroke)
            else:
                # default to cross
                svg.add_line(
                    x1=x1 - s, y1=y1, x2=x1 + s, y2=y1, color=color, stroke=stroke
                )
                svg.add_line(
                    x1=x1, y1=y1 - s, x2=x1, y2=y1 + s, color=color, stroke=stroke
                )

    if show_axes:
        graph.add_x_axis(svg, axis=xaxis, pos=(0, h))
        graph.add_y_axis(svg, axis=yaxis)
        # add_survival_axes(svg, axes, type)

    return df, kmf


def add_survival_axes(
    svg: SVGFigure, axes: tuple[Axis, Axis], type: str = "OS"
) -> None:
    xaxis, yaxis = axes
    h = yaxis.w

    # add_years_axis(svg, axis=xaxis, y=h)
    graph.add_x_axis(svg, axis=xaxis, pos=(0, h))
    graph.add_y_percent_axis(svg, axis=yaxis, label=type)


def add_survival_legend(
    svg: SVGFigure,
    name: str,
    color: str,
    pos: tuple[float, float] = (0, 0),
    padding: Union[int, float] = 10,
    censor_kws: Mapping[str, Union[int, float, bool, str]] = None,
    stroke: int = 4,
) -> None:
    x, y = pos

    _censor_kws = _get_censor_kws(censor_kws)

    if isinstance(name, str):
        name = [name]

    h = (svg.get_font_h() + padding) * len(name)
    h2 = (svg.get_font_h() + padding) * (len(name) - 1) / 2

    x1 = x
    x2 = x1 + _censor_kws["size"] * 4
    x3 = (x1 + x2) / 2

    svg.add_line(x1=x1, y1=y + h2, x2=x2, y2=y + h2, color=color, stroke=stroke)

    if _censor_kws["show"]:
        s = _censor_kws["size"]

        if _censor_kws["shape"] == "x":
            l = math.sin(math.pi / 2) * s
            svg.add_line(
                x1=x3 - l, y1=y - l, x2=x3 + l, y2=y + l, color=color, stroke=stroke
            )
            svg.add_line(
                x1=x3 - l, y1=y + l, x2=x3 + l, y2=y - l, color=color, stroke=stroke
            )
        elif _censor_kws["shape"] == "|":
            svg.add_line(x1=x3, y1=y, x2=x3, y2=y - s, color=color, stroke=stroke)
        else:
            svg.add_line(x1=x3, y1=y - s, x2=x3, y2=y + s, color=color, stroke=stroke)

    for t in name:
        svg.add_text_bb(t, x=x + 40, y=y, color=color)
        y += svg.get_font_h() + padding

    return h


def add_years_axis(
    svg: SVGFigure,
    axis: Axis = Axis(lim=(0, 18), ticks=[0, 3, 6, 9, 12, 15, 18]),
    x: int = 0,
    y: int = 0,
) -> None:
    graph.add_x_axis(
        svg,
        axis=axis,
        pos=(0, y),
        # minorticks=range(1, 18),
        label="Years",
    )

    return axis


# def plot_survival(svg: SVGFigure,
#                   file: str,
#                   axes: tuple[Axis, Axis],
#                   x: int = 0,
#                   y: int = 0,
#                   type: str = 'OS',
#                   show_ci: bool = False,
#                   ci_fill_opacity: float = 0.2,
#                 censor_kws: Mapping[str, Union[int, float, bool, str]] = None,
#                   stroke=4) -> None:

#     _censor_kws = _get_censor_kws(censor_kws)

#     with open(file, 'r') as f:
#         jd = json.load(f)

#     xaxis, yaxis = axes
#     h = yaxis.w

#     for jd1 in jd:
#         print(jd1['name'])

#         if len(jd1['data'][0]) == 5:
#             df = pd.DataFrame(jd1['data'], columns=[
#                 'x', 'y', 'censored', 'ci_low', 'ci_high'])
#         else:
#             df = pd.DataFrame(jd1['data'], columns=[
#                 'x', 'y', 'censored', -1, -1])

#         df['y'] = (1 - df['y']) * 100
#         df['ci_low'] = df['ci_low'] * 100
#         df['ci_high'] = df['ci_high'] * 100

#         if show_ci:
#             points = [[df['x'].values[0], df['ci_high'].values[0]]]

#             for i2 in range(1, df.shape[0]):
#                 x1, y1 = points[-1]
#                 x2, y2, censored2, ci_low2, ci_high2 = df.iloc[i2, :].values

#                 # need to modify x to ensure only right angles
#                 if y1 != ci_high2:
#                     points.append([x2, y1])

#                 points.append([x2, ci_high2])

#             points.append([df['x'].values[-1], df['ci_low'].values[-1]])

#             for i2 in range(df.shape[0] - 2, -1, -1):
#                 x1, y1 = points[-1]
#                 x2, y2, censored2, ci_low2, ci_high2 = df.iloc[i2, :].values

#                 if y1 != ci_low2:
#                     points.append([x2, y1])

#                 points.append([x2, ci_low2])

#             # so they are on axes scales
#             points = [
#                 [x + xaxis.scale(x1), y + yaxis.w - yaxis.scale(y1)] for x1, y1 in points]
#             svg.add_polygon(
#                 points, fill=jd1['color'], fill_opacity=ci_fill_opacity)

#         d = [df.iloc[0, :].values]

#         for i2 in range(1, df.shape[0]):
#             x1, y1, censored1, ci_low1, ci_high1 = d[-1]
#             x2, y2, censored2, ci_low2, ci_high2 = df.iloc[i2, :].values

#             #d.append(df.iloc[i1, :].values)

#             if y1 != y2:
#                 # to prevent lines at angles other than 90
#                 # insert an extra point with the same x as
#                 # the current spot, but the y of the previous
#                 # spot
#                 d.append([x2, y1, 0, ci_low1, ci_high1])

#             d.append([x2, y2, censored2, ci_low2, ci_high2])

#         df1 = pd.DataFrame(
#             d, columns=['x', 'y', 'censored', 'ci_low', 'ci_high'])

#         c = jd1['color']

#         svg.add_lineplot_v2(df1,
#                             color=c,
#                             axes=[xaxis, yaxis],
#                             xaxis_kws={'show': False},
#                             yaxis_kws={'show': False},
#                             stroke=stroke)

#         if _censor_kws['show']:
#             # show censors as a cross
#             dfc = df[df['censored'] == 1]

#             for i in range(0, dfc.shape[0]):
#                 x1 = xaxis.scale(dfc['x'].values[i])
#                 y1 = y + h - yaxis.scale(dfc['y'].values[i])
#                 s = _censor_kws['size']

#                 match _censor_kws['shape']:
#                     case 'x':
#                         l = math.sin(math.pi/2) * s
#                         svg.add_line(
#                             x1=x1-l, y1=y1-l, x2=x1+l, y2=y1+l, color=c, stroke=stroke)
#                         svg.add_line(
#                             x1=x1-l, y1=y1+l, x2=x1+l, y2=y1-l, color=c, stroke=stroke)
#                     case '|':
#                         svg.add_line(
#                             x1=x1, y1=y1, x2=x1, y2=y1-s, color=c, stroke=stroke)
#                     case _:
#                         # default to cross
#                         svg.add_line(x1=x1-s, y1=y1, x2=x1 +
#                                      s, y2=y1, color=c, stroke=stroke)
#                         svg.add_line(x1=x1, y1=y1-s, x2=x1, y2=y1 +
#                                      s, color=c, stroke=stroke)

#     add_years_axis(svg, axis=xaxis, y=h)
#     svg.add_y_percent_axis(axis=yaxis, label=type)
