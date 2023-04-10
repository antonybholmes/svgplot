from typing import Mapping, Optional, Union, Any
from collections.abc import Iterable
from .axis import Axis
from .svgfigure import SVGFigure
from . import svgfiguredraw
import numpy as np
import math

STROKE_SIZE = 2
TICK_SIZE = 10
MINOR_TICK_SIZE = TICK_SIZE - 4
AXIS_STROKE = 2
MINOR_TICK_STROKE = 2


def _get_fill_kws(kws: Mapping[str, Union[int, float, bool, str]]) -> dict[str, Union[int, float, bool, str]]:
    if kws is None:
        kws = {}

    ret = {'show': True, 'shape': 'x', 'size': 8}
    ret.update(kws)
    return ret


def _get_default_x_kws(kws: Mapping[str, Union[int, float, bool, str]] = {}) -> Mapping[str, Union[int, float, bool, str]]:
    ret = {'show': True, 'label': True, 'stroke': 3, 'title_offset': 70,
           'ticklabeloffset':0,
           'clip': True, 'label_pos': 'c', 'invert': False}
    ret.update(kws)
    return ret


def _get_default_y_kws(kws: Mapping[str, Union[int, float, bool, str]] = {}) -> Mapping[str, Union[int, float, bool, str]]:
    ret = {'show': True, 'label': True, 'stroke': 3, 'title_offset': 120,'ticklabeloffset':0,
           'clip': True, 'label_pos': 'c', 'invert': False}
    ret.update(kws)
    return ret


def _get_default_axes_kws(xaxis_kws: Mapping[str, Union[int, float, bool, str]] = {},
                          yaxis_kws: Mapping[str, Union[int, float, bool, str]] = {}) -> list[Mapping[str, Union[int, float, bool, str]]]:
    return (_get_default_x_kws(xaxis_kws), _get_default_y_kws(yaxis_kws))


def add_axes(svg: SVGFigure,
             pos: tuple[float, float] = (0, 0),
             axes: tuple[Axis, Axis] = None,
             xaxis_kws: Optional[Union[bool, str, Mapping[str,
                                                          Union[int, float, str, bool]]]] = None,
             yaxis_kws: Optional[Union[bool, str, Mapping[str, Union[int, float, str, bool]]]] = None) -> None:
    x, y = pos

    xaxis, yaxis = axes

    # set some defaults
    _show_axes = _get_default_axes_kws(xaxis_kws, yaxis_kws)

    if _show_axes[0]['show']:
        y1 = y

        if not _show_axes[1]['invert']:
            y1 = y + yaxis.w

        add_x_axis(svg,
                   pos=(x, y1),
                   axis=xaxis,
                   ticks=xaxis.ticks,
                   ticklabels=xaxis.ticklabels,
                   showticks=True,
                   stroke=_show_axes[0]['stroke'],
                   showlabel=_show_axes[0]['label'],
                   title_offset=_show_axes[0]['title_offset'],
                   label_pos=_show_axes[0]['label_pos'],
                   ticklabel_offset=_show_axes[0]['ticklabeloffset'])

        # if _show_axes[0]['label']:
        #     svg.add_text_bb(xaxis.label, x=xaxis.w/2, y=y1 +
        #                     _show_axes[0]['title_offset'], align='c')

    if _show_axes[1]['show']:
        add_y_axis(svg,
                   pos=pos,
                   axis=yaxis,
                   ticks=yaxis.ticks,
                   ticklabels=yaxis.ticklabels,
                   showticks=True,
                   stroke=_show_axes[1]['stroke'],
                   showlabel=_show_axes[1]['label'],
                   title_offset=_show_axes[1]['title_offset'],
                   invert=_show_axes[1]['invert'])

        # if show_axes[1]['label']:
        #    svg.add_text_bb(yaxis.label, x=-60, y=y+yaxis.w/2, align='c', orientation='v')

    return xaxis.w, yaxis.w


def add_x_axis(svg,
               pos: tuple[Union[int, float], Union[int, float]] = (0, 0),
               axis: Axis = Axis(lim=[0, 100], w=200, ticks=[
                                 0, 20, 40, 60, 80, 100]),
               ticks: Optional[Iterable[Union[int, float]]] = None,
               ticklabels: Optional[Iterable[Union[str, int, float]]] = None,
               label: Optional[str] = None,
               padding: int = TICK_SIZE,
               showticks: bool = True,
               inside: bool = False,
               showline: bool = True,
               minorticks: Optional[Iterable[Union[int, float]]] = None,
               ticksize: int = TICK_SIZE,
               minorticksize: int = MINOR_TICK_SIZE,
               stroke: int = AXIS_STROKE,
               tickstroke: Optional[int] = None,
               minortickstroke: Optional[int] = None,
               invert: bool = False,
               showlabel: bool = True,
               title_offset: Optional[int] = None,
               label_pos: str = 'center',
               ticklabel_offset:int = 0):

    x, y = pos

    if tickstroke is None:
        tickstroke = stroke

    if minortickstroke is None:
        minortickstroke = stroke

    if label is None:
        label = axis.label

    # if smallfont:
    #    svg.set_font_size(FIGURE_FONT_SIZE)

    # svg.set_font_size(9)

    if ticklabels is None:
        if ticks is not None:
            ticklabels = ticks
        else:
            ticklabels = axis.ticklabels

    if ticks is None:
        ticks = axis.ticks

    if invert:
        x1 = x - stroke / 2
        x2 = x - axis.w - stroke / 2
    else:
        x1 = x - stroke / 2
        x2 = x + axis.w + stroke / 2

    if showline:
        svg.add_line(x1=x1, y1=y, x2=x2, y2=y, stroke=stroke)

    for i in range(0, len(ticks)):
        tick = ticks[i]

        if tick < axis.lim[0] or tick > axis.lim[1]:
            continue

        if invert:
            tickx = x - axis.scale(tick)
        else:
            tickx = x + axis.scale(tick)  # (tick - ylim[0]) / yrange * h

        ticklabel = ticklabels[i]

        if not isinstance(ticklabel, str):
            ticklabel = str(ticklabel)

        if showticks:
            if inside:
                svg.add_line(x1=tickx, y1=y-ticksize,
                             x2=tickx, y2=y, stroke=tickstroke)
                y1 = y + svg.get_font_h()
            else:
                svg.add_line(x1=tickx, y1=y, x2=tickx, y2=y +
                             ticksize, stroke=tickstroke)
                y1 = y + ticksize / 2 + svg.get_font_h() + ticklabel_offset

            if label_pos == 'inner':
                align = 'r' if i == len(ticks) - 1 else 'l'
                svg.add_text_bb(ticklabel, x=tickx, y=y1, align=align)
            else:
                #print(tickx, ticklabel)
                svg.add_text_bb(ticklabel, x=tickx, y=y1, align='c')
                #pass
        else:
            svg.add_text_bb(ticklabel, x=tickx, y=y +
                            svg.get_font_h() + ticklabel_offset, align='c')

    if minorticks is not None:
        for i in range(0, len(minorticks)):
            tick = minorticks[i]

            if tick < axis.lim[0] or tick > axis.lim[1]:
                continue

            if invert:
                tickx = x - axis.scale(tick)  # (tick - ylim[0]) / yrange * h
            else:
                tickx = x + axis.scale(tick)

            if showticks:
                if inside:
                    svg.add_line(x1=tickx, y1=y-minorticksize,
                                 x2=tickx, y2=y, stroke=minortickstroke)
                else:
                    svg.add_line(x1=tickx, y1=y, x2=tickx, y2=y +
                                 minorticksize, stroke=minortickstroke)

    if showlabel and isinstance(label, str) and label != "":
        if title_offset is None:
            if showticks:
                title_offset = 2*padding+2*svg.get_font_h()
            else:
                title_offset = padding+2*svg.get_font_h()

        if invert:
            x1 = x - axis.w
        else:
            x1 = x

        if showticks:
            svg.add_text_bb(label, x=x1, y=y+title_offset, w=axis.w, align='c')
        else:
            svg.add_text_bb(label, x=x1, y=y+title_offset, w=axis.w, align='c')

    # svg.set_font_size(DEFAULT_FONT_SIZE)


def add_y_axis(svg,
               pos: tuple[Union[int, float], Union[int, float]] = (0, 0),
               axis: Axis = Axis(lim=[0, 100], w=200),
               ticks: Optional[Iterable[Union[int, float]]] = None,
               ticklabels: Optional[Iterable[Union[str, int, float]]] = None,
               label: Optional[str] = None,
               padding: int = TICK_SIZE,
               showticks: bool = True,
               inside: bool = False,
               showline: bool = True,
               side: str = 'l',
               stroke: int = AXIS_STROKE,
               minorticks: Optional[Iterable[Union[int, float]]] = None,
               ticksize: int = TICK_SIZE,
               tickstroke: Optional[int] = None,
               minorticksize: int = MINOR_TICK_SIZE,
               minortickstroke: Optional[int] = None,
               title_offset: Optional[int] = None,
               tickcolor: str = 'black',
               showlabel: bool = True,
               invert: bool = False):

    x, y = pos

    if tickstroke is None:
        tickstroke = stroke

    if minortickstroke is None:
        minortickstroke = stroke

    if ticklabels is None:
        if ticks is not None:
            # if ticks specified, use these as labels
            ticklabels = ticks
        else:
            # pick the labels from the axis object
            ticklabels = axis.ticklabels

    if ticks is None:
        # use the axis ticks by default
        ticks = axis.ticks

    if ticklabels is None:
        ticklabels = ticks

    if label is None:
        label = axis.label

    mw = 0

    if showline:
        svg.add_line(x1=x, y1=y-stroke/2, y2=y+axis.w +
                     stroke/2, x2=x, stroke=stroke)

    for i in range(0, len(ticks)):
        tick = ticks[i]

        if tick < axis.lim[0] or tick > axis.lim[1]:
            continue

        if invert:
            ticky = y + axis.scale(tick)
        else:
            ticky = y + axis.w - axis.scale(tick)

        #print(i, ticklabels)
        ticklabel = ticklabels[i]

        if not isinstance(ticklabel, str):
            ticklabel = str(ticklabel)

        if showticks:
            if inside:
                if side == 'r':
                    svg.add_line(x1=x-ticksize, y1=ticky, x2=x,
                                 y2=ticky, stroke=tickstroke)
                    svg.add_text_bb(ticklabel, x=x+ticksize,
                                    y=ticky, color=tickcolor)
                else:
                    svg.add_line(x1=x, y1=ticky, x2=x+ticksize,
                                 y2=ticky, stroke=tickstroke)
                    svg.add_text_bb(ticklabel, x=x-ticksize,
                                    y=ticky, align='r', color=tickcolor)
            else:
                if side == 'r':
                    svg.add_line(x1=x, y1=ticky, x2=x+ticksize,
                                 y2=ticky, stroke=tickstroke)
                    svg.add_text_bb(ticklabel, x=x+2*ticksize,
                                    y=ticky, color=tickcolor)
                else:
                    svg.add_line(x1=x-ticksize, y1=ticky, x2=x,
                                 y2=ticky, stroke=tickstroke)
                    svg.add_text_bb(ticklabel, x=x-2*ticksize,
                                    y=ticky, align='r', color=tickcolor)
        else:
            if side == 'r':
                svg.add_text_bb(ticklabel, x=x+ticksize,
                                y=ticky, color=tickcolor)
            else:
                svg.add_text_bb(ticklabel, x=x-padding, y=ticky,
                                align='r', color=tickcolor)

        mw = max(mw, svg.get_string_width(ticklabel))

    if minorticks is not None:
        for i in range(0, len(minorticks)):
            tick = minorticks[i]

            if tick < axis.lim[0] or tick > axis.lim[1]:
                continue

            if invert:
                ticky = y + axis.scale(tick)  # (tick - ylim[0]) / yrange * h
            else:
                ticky = y + axis.w - axis.scale(tick)

            if showticks:
                if inside:
                    if side == 'r':
                        svg.add_line(x1=x-minorticksize, y1=ticky,
                                     x2=x, y2=ticky, stroke=minortickstroke)
                    else:
                        svg.add_line(x1=x, y1=ticky, x2=x+minorticksize,
                                     y2=ticky, stroke=minortickstroke)
                else:
                    if side == 'r':
                        svg.add_line(x1=x, y1=ticky, x2=x+minorticksize,
                                     y2=ticky, stroke=minortickstroke)
                    else:
                        svg.add_line(x1=x-minorticksize, y1=ticky,
                                     x2=x, y2=ticky, stroke=minortickstroke)

    if showlabel and isinstance(label, str) and label != "":
        if title_offset is None:
            title_offset = max(80, mw + 20 + 4 * padding)

        y1 = y + axis.w / 2

        svg.add_text_bb(label,
                        x=x-title_offset,
                        y=y1,
                        align='c',
                        orientation='v')

    # svg.set_font_size(DEFAULT_FONT_SIZE)


def add_y_percent_axis(svg,
                       axis: Axis = Axis(lim=[0, 100], w=200),
                       pos: tuple[float, float] = (0, 0),
                       ticks=[0, 20, 40, 60, 80, 100],
                       minorticks=None,  # range(5, 100, 5),
                       label: str = ''):
    add_y_axis(svg,
               axis=axis,
               pos=pos,
               ticks=ticks,
               label=label + ' (%)',
               # ['0%', '20%', '40%', '60%', '80%', '100%'],
               ticklabels=ticks,
               minorticks=minorticks)
