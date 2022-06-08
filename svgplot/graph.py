from typing import Mapping, Optional, Union
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
           'clip': False, 'label_pos': 'c', 'invert': False}
    ret.update(kws)
    return ret


def _get_default_y_kws(kws: Mapping[str, Union[int, float, bool, str]] = {}) -> Mapping[str, Union[int, float, bool, str]]:
    ret = {'show': True, 'label': True, 'stroke': 3, 'title_offset': 120,
           'clip': False, 'label_pos': 'c', 'invert': False}
    ret.update(kws)
    return ret


def _get_default_axes_kws(xaxis_kws: Mapping[str, Union[int, float, bool, str]] = {},
                          yaxis_kws: Mapping[str, Union[int, float, bool, str]] = {}) -> list[Mapping[str, Union[int, float, bool, str]]]:
    return (_get_default_x_kws(xaxis_kws), _get_default_y_kws(yaxis_kws))


def add_pie_chart(svg: SVGFigure,
                  values: list[float],
                  colors: list[str] = None,
                  labels: list[str] = None,
                  labelcolors='white',
                  labelradius=0.5,
                  edgecolor='black',
                  pos: tuple[float, float] = (0, 0),
                  r: int = 150,
                  labelrmap={},
                  stroke=2):
    x, y = pos

    if colors is None:
        colors = ['blue']

    if labels is not None:
        labels = np.array(labels)

    if isinstance(labelcolors, str):
        labelcolors = [labelcolors]

    labelcolors = np.array(labelcolors)

    colors = np.array(colors)

    fracs = np.array(values)
    fracs = fracs / fracs.sum()

    print(fracs)

    angle1 = 0
    angle2 = 0
    labelradius = r * labelradius

    for i in range(0, fracs.size):
        f = fracs[i]
        angle2 = round(360 * f)

        # svgplot.rgbtohex(colors[i % colors.size])
        col = colors[i % colors.size]

        svg.add_arc(x=x, y=y, w=r*2, h=r*2, angle1=angle1,
                    angle2=angle2, fill=col, color=edgecolor, stroke=stroke)

        angle3 = (angle1 + angle2) / 2
        angle3 = angle3 / 360 * svgfiguredraw.TWO_PI_RADS

        angle1 += angle2

        # break

    if labels is not None:
        angle1 = 0
        angle2 = 0

        for i in range(0, fracs.size):
            f = fracs[i]
            angle2 = round(360 * f)

            angle3 = angle1 + angle2 / 2

            angle4 = angle3 / 360 * svgfiguredraw.TWO_PI_RADS

            lr = labelradius

            if i in labelrmap:
                lr *= labelrmap[i]

            if angle3 > 270:
                x1 = x + lr * math.sin(angle4)
                y1 = y - lr * math.cos(angle4)
            elif angle3 > 180:
                x1 = x + lr * math.sin(angle4)
                y1 = y - lr * math.cos(angle4)
            elif angle3 > 90:
                x1 = x + lr * math.sin(angle4)
                y1 = y - lr * math.cos(angle4)
            else:
                x1 = x + lr * math.sin(angle4)
                y1 = y - lr * math.cos(angle4)

            svg.add_text_bb(labels[i % labels.size], x=x1, y=y1,
                            align='c', color=labelcolors[i % labelcolors.size])

            angle1 += angle2


def add_stacked_bar(svg: SVGFigure,
                    tables,
                    bar_colors={},
                    x=0,
                    y=0,
                    height=400,
                    bar_width=60,
                    bar_padding=10,
                    bar_color='#cccccc',
                    ylim=[0, 100],
                    yticks=[0, 50, 100],
                    xlabel='',
                    ylabel='% cells',
                    padding=10,
                    whisker=20,
                    as_pc=True):
    # self.set_font_size(svgplot.FIGURE_FONT_SIZE)

    if as_pc:
        pc_tables = [(t / t.sum(axis=0) * 100) for t in tables]
        yaxis = Axis(lim=[0, 100], w=height)
    else:
        pc_tables = tables
        yaxis = Axis(lim=ylim, w=height)

    block_size = bar_width + 2 * bar_padding

    #w = means.size * block_size

    #xaxis = axis.Axis(lim=[0, df.shape[1]], w=w)

    y2 = y + height

    # draw bars

    x1 = x + bar_padding

    for t in pc_tables:
        for c in range(0, t.shape[1]):
            y3 = y2
            for r in range(t.shape[0] - 1, -1, -1):
                h = yaxis.scale(t.iloc[r, c])
                y1 = y3 - h

                bar_name = str(t.index[r])

                if bar_name in bar_colors:
                    bar_color = bar_colors[bar_name]
                else:
                    bar_color = 'gray'

                svg.add_rect(x1, y1, bar_width, h, fill=bar_color)
                svg.add_rect(x1, y1, bar_width, h, color='black')
                y3 -= h
            x1 += block_size

    add_y_axis(svg, axis=yaxis, pos=(0, 0), ticks=yticks, label=ylabel)

    # # draw xaxis
    #self.add_line(x1=x, y1=y+h, x2=x + df.shape[1] * block_size, y2=y+h)

    # # draw sd

    # x1 = x + bar_padding + bar_width / 2

    # for i in range(0, means.size):
    #     y1 = y2 - yaxis.scale(means[i])

    #     ysd = yaxis.scale(sds[i])

    #     yb1 = y1 - ysd

    #     # stop bars dropping below x axis
    #     yb2 = min(y2, y1 + ysd)

    #     self.add_line(x1=x1, y1=yb1, x2=x1, y2=yb2)

    #     xb1 = x1 - whisker / 2
    #     xb2 = xb1 + whisker

    #     self.add_line(x1=xb1, y1=yb1, x2=xb2, y2=yb1)

    #     if (y1 + ysd) < y2 - 20:
    #         self.add_line(x1=xb1, y1=yb2, x2=xb2, y2=yb2)

    #     x1 += block_size

    # self.add_y_axis(axis=yaxis, y=y+h, ticks=[0, 50, 100], label='% cells')

    # # draw xaxis
    # self.add_line(x1=x, y1=y+h, x2=x + df.shape[1] * block_size, y2=y+h)

    # x1 = x
    # for i in range(0, df.shape[1]):
    #     y1 = h - yaxis.scale(means[i]) - yaxis.scale(sds[i]) - self.get_font_h()

    #     self.add_text_bb('{}%'.format(
    #         round(means[i], 1)), x=x1, y=y1, w=block_size, align='c')

    #     x1 += block_size

    # rows = df.columns[0].replace('+', '').replace('-', '').split(' ')

    # d = np.empty((len(rows), df.shape[1]), dtype=object)

    # for j in range(0, df.shape[1]):
    #     names = df.columns[j].split(' ')

    #     for i in range(0, len(names)):
    #         name = names[i]

    #         if '+' in name:
    #             d[i, j] = '+'
    #         else:
    #             d[i, j] = '-'

    # self.inc(y=y2 + 50)

    # self.set_font_size(svgplot.DEFAULT_FONT_SIZE)

    # for i in range(0, len(rows)):
    #     self.add_text_bb(rows[i], x=0, align='r')

    #     x1 = 0

    #     for j in range(0, df.shape[1]):
    #         self.add_text_bb(d[i, j], x=x1, w=block_size, align='c')
    #         #self.add_frame(x, 0, xd, 20, color='red')
    #         x1 += block_size

    #     self.inc(y=self.get_font_h() + 10)


def add_axes(svg: SVGFigure,
             pos: tuple[float, float] = (0, 0),
             axes: tuple[Axis, Axis] = None,
             xaxis_kws: Optional[Union[bool, str, Mapping[str,
                                                          Union[int, float, str, bool]]]] = None,
             yaxis_kws: Optional[Union[bool, str, Mapping[str, Union[int, float, str, bool]]]] = None) -> None:
    x, y = pos

    if axes is None:
        axes = (Axis(lim=(0, 100), w=200), Axis(lim=(0, 100), w=200))

    xaxis = axes[0]
    yaxis = axes[1]

    # set some defaults
    _show_axes = _get_default_axes_kws(xaxis_kws, yaxis_kws)

    if isinstance(xaxis_kws, dict):
        _show_axes[0].update(xaxis_kws)
    elif isinstance(xaxis_kws, bool):
        _show_axes[0]['show'] = xaxis_kws
    elif isinstance(xaxis_kws, str):
        _show_axes[0]['show'] = 'show' in xaxis_kws[0]
    else:
        pass

    if isinstance(yaxis_kws, dict):
        _show_axes[1].update(yaxis_kws)
    elif isinstance(yaxis_kws, bool):
        _show_axes[1]['show'] = yaxis_kws
    elif isinstance(yaxis_kws, str):
        _show_axes[1]['show'] = 'show' in yaxis_kws[0]
    else:
        pass

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
                   label_pos=_show_axes[0]['label_pos'])

        if _show_axes[0]['label']:
            svg.add_text_bb(xaxis.label, x=xaxis.w/2, y=y1 +
                            _show_axes[0]['title_offset'], align='c')

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
               pos: tuple[float, float] = (0, 0),
               axis: Axis = Axis(lim=[0, 100], w=200, ticks=[
                                 0, 20, 40, 60, 80, 100]),
               ticks=None,
               ticklabels=None,
               label=None,
               padding=TICK_SIZE,
               showticks=True,
               inside=False,
               showline=True,
               minorticks=None,
               ticksize=TICK_SIZE,
               minorticksize=MINOR_TICK_SIZE,
               stroke=AXIS_STROKE,
               tickstroke=None,
               minortickstroke=None,
               invert=False,
               showlabel=True,
               title_offset=None,
               label_pos='center'):

    x, y = pos

    if tickstroke is None:
        tickstroke = stroke

    if minortickstroke is None:
        minortickstroke = stroke

    # if smallfont:
    #    svg.set_font_size(FIGURE_FONT_SIZE)

    # svg.set_font_size(9)

    if ticks is None:
        ticks = axis.ticks

    if ticklabels is None:
        ticklabels = axis.ticklabels

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
                y1 = y + ticksize / 2 + svg.get_font_h()

            if label_pos == 'inner':
                align = 'r' if i == len(ticks) - 1 else 'l'
                svg.add_text_bb(ticklabel, x=tickx, y=y1, align=align)
            else:
                svg.add_text_bb(ticklabel, x=tickx, y=y1, align='c')
        else:
            svg.add_text_bb(ticklabel, x=tickx, y=y +
                            svg.get_font_h(), align='c')

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

    if showlabel and isinstance(label, str):
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
               pos: tuple[float, float] = (0, 0),
               axis: Axis = Axis(lim=[0, 100], w=200),
               ticks: Optional[list[float]] = None,
               ticklabels: Optional[list[Union[int, float, str]]] = None,
               label: str = None,
               padding: int = TICK_SIZE,
               showticks: bool = True,
               inside: bool = False,
               showline: bool = True,
               side: str = 'l',
               stroke: int = AXIS_STROKE,
               minorticks: Optional[list[float]] = None,
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

    if ticks is None:
        ticks = axis.ticks

    if ticklabels is None:
        ticklabels = axis.ticklabels

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

    if showlabel and isinstance(label, str):
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
                       label: str = None):
    add_y_axis(svg,
               axis=axis,
               pos=pos,
               ticks=ticks,
               label=label + ' (%)',
               # ['0%', '20%', '40%', '60%', '80%', '100%'],
               ticklabels=[0, 20, 40, 60, 80, 100],
               minorticks=minorticks)
