#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: antony
"""
import numpy as np
from typing import Optional, Union
import libplot
import matplotlib
import pandas as pd
import lib10x
from . import core
from .svgfigure import SVGFigure

DEFAULT_CELL = (50, 50)
DEFAULT_COLORBAR_CELL = (50, 25)
DEFAULT_LIMITS = (-2, 2)


def add_heatmap(svg: SVGFigure,
                df: pd.DataFrame,
                pos: tuple[int, int] = (0, 0),
                cell: tuple[int, int] = DEFAULT_CELL,
                lim: tuple[int, int] = DEFAULT_LIMITS,
                cmap = libplot.BWR2_CMAP,
                gridcolor=core.GRID_COLOR,
                showframe: bool = True,
                xticklabels: Optional[Union[list[str], bool]] = True,
                xticklabel_colors: dict[str, str] = {},
                yticklabels: Optional[Union[list[str], bool]] = True,
                yticklabel_colors: dict[str, str] = {},
                col_colors: dict[str, str] = {},
                color_height=0,
                rename_cols: dict[str, str] = {},
                row_zscore: bool = False,
                xsplits=[],
                xsplitgap=40,
                ysplits=[],
                ysplitgap=40):
    """
    Draws a heat map.

    Args:
        svg (SVGFigure): _description_
        df (pd.DataFrame): table data to render.
        pos (tuple[int, int], optional): Offset to render heat map at. Defaults to (0, 0).
        cell (tuple[int, int], optional): Size of heat map cell. Defaults to DEFAULT_CELL.
        lim (tuple[int, int], optional): _description_. Defaults to DEFAULT_LIMITS.
        cmap (_type_, optional): _description_. Defaults to libplot.BWR2_CMAP.
        gridcolor (_type_, optional): _description_. Defaults to core.GRID_COLOR.
        showframe (bool, optional): _description_. Defaults to True.
        xticklabels (Optional[Union[list[str], bool]], optional): _description_. Defaults to True.
        xticklabel_colors (dict[str, str], optional): _description_. Defaults to {}.
        yticklabels (Optional[Union[list[str], bool]], optional): _description_. Defaults to True.
        row_zscore (bool, optional): _description_. Defaults to False.

    Returns:
        tuple[int, int, dict[int, int]]: width and height of plot and map of row to y position.
    """

    x, y = pos

    if row_zscore:
        df = lib10x.scale(df)

    if isinstance(xticklabels, bool):
        if xticklabels:
            xticklabels = df.columns
        else:
            xticklabels = []

    if isinstance(yticklabels, bool):
        if yticklabels:
            yticklabels = df.index
        else:
            yticklabels = []

    mapper = matplotlib.cm.ScalarMappable(
        norm=matplotlib.colors.Normalize(vmin=lim[0], vmax=lim[1]), cmap=cmap)

    w = cell[0] * df.shape[1]

    # the last/only split is the last row so the block
    # always goes from the start/last split to the end row
    if len(xsplits) == 0 or xsplits[-1] != df.shape[1]:
        xsplits.append(df.shape[1])

    # the last/only split is the last row so the block
    # always goes from the start/last split to the end row
    if len(ysplits) == 0 or ysplits[-1] != df.shape[0]:
        ysplits.append(df.shape[0])

    # track y location of each row, useful for fixing
    # dendrograms or other plot elements that sync to
    # row positions
    x_map = {}
    y_map = {}

    xs1 = 0
    x1 = x

    for xs2 in xsplits:
        ys1 = 0
        y1 = y

        for ys2 in ysplits:
            x2 = x1

            for xi in range(xs1, xs2):
                y2 = y1

                for yi in range(ys1, ys2):
                    v = df.iloc[yi, xi]
                    color = core.rgbatohex(mapper.to_rgba(v))
                    svg.add_rect(x2, y2, cell[0], cell[1], fill=color)

                    y_map[yi] = y2
                    y2 += cell[1]
                x_map[xi] = x2
                x2 += cell[0]

            if gridcolor is not None:
                add_grid(svg,
                        pos=(x1, y1),
                        size=(x2 - x1, y2 - y1),
                        shape=(ys2 - ys1, xs2 - xs1),
                        color=gridcolor)

            if showframe:
                svg.add_frame(x=x1, y=y1, w=x2-x1, h=y2-y1)

            ys1 = ys2
            y1 = y2 + ysplitgap

        xs1 = xs2
        x1 = x2 + xsplitgap


    w = x1 - xsplitgap
    h = y1 - ysplitgap  # cell[1] * df.shape[0]

    if len(yticklabels) > 0:
        y1 = y
        ys1 = 0
        for ys2 in ysplits:
            labels = yticklabels[ys1:ys2]
            add_yticklabels(svg, yticklabels[ys1:ys2], cell=cell, pos=(w+20, y1), colors=yticklabel_colors)
            ys1 = ys2
            y1 += cell[1] * len(labels) + ysplitgap


    
    if len(xticklabels) > 0:
        x1 = x
        xs1 = 0
        y1 = y - 30

        if color_height > 0 and len(col_colors) > 0:
            y1 -= (color_height + 30)

        for xs2 in xsplits:
            labels = df.columns[xs1:xs2]
            #labels = np.array([rename_cols[x] if x in rename_cols else x for x in labels])

            add_xticklabels(svg, labels, pos=(x1, y1), colors=xticklabel_colors, rename_cols=rename_cols)
            
            x1 += cell[0] * labels.size + xsplitgap
            xs1 = xs2

        #add_xticklabels(svg, xticklabels, cell=cell, colors=xticklabelcolors)

    if color_height > 0 and len(col_colors) > 0:
        x1 = x
        xs1 = 0
        y1 = y - 30 - color_height

        x1 = x
        xs1 = 0
        for xs2 in xsplits:
            labels = df.columns[xs1:xs2]
            #labels = np.array([rename_cols[x] if x in rename_cols else x for x in labels])

            x2 = x1
            for i, c in enumerate(labels):
                for name in col_colors:
                    if name in c:
                        svg.add_rect(x2, y1, cell[0] * (labels.size - i), color_height,
                                    fill=col_colors[name])
                        break
                x2 += cell[0]

            svg.add_frame(x=x1, y=y1, w=x2-x1, h=color_height)
            
            x1 = x2 + xsplitgap
            xs1 = xs2

    return {'w':w, 'h':h, 'x_map':x_map, 'y_map':y_map}


def add_xticklabels(svg: SVGFigure,
                    labels: Union[pd.DataFrame, list[str]],
                    colors: dict[str, str] = {},
                    pos: tuple[int, int] = (0, -30),
                    cell: tuple[int, int] = DEFAULT_CELL,
                    default_color: str = 'black',
                    rename_cols: dict[str, str] = {}):
    if isinstance(labels, pd.DataFrame):
        labels = labels.columns

    if len(labels) == 0:
        return

    x, y = pos

    x1 = x + cell[0] / 2

    for name in labels:
        color = default_color
        
        # this is to allow for partial matches to column names
        # but it is less efficient than a simple lookup
        if len(colors) > 0:
            for label, c in colors.items():
                if label in name:
                    color = c
                    break


        svg.add_text_bb(rename_cols.get(name, name), x=x1, y=y, orientation='v', color=color)
        x1 += cell[0]


def add_yticklabels(svg: SVGFigure,
                    labels: Union[pd.DataFrame, list[str]],
                    colors: dict[str, str] = {},
                    pos: tuple[int, int] = (0, 0),
                    cell: tuple[int, int] = DEFAULT_CELL,
                    default_color: str = 'black'):
    if isinstance(labels, pd.DataFrame):
        labels = labels.index

    if len(labels) == 0:
        return

    x, y = pos

    y1 = y + cell[1] / 2

    for name in labels:
        color = default_color

        if len(colors) > 0:
            for label, c in colors.items():
                if label in name:
                    color = c
                    break

        svg.add_text_bb(name, x=x, y=y1, color=color)
        y1 += cell[1]


def add_col_colorbar(svg: SVGFigure,
                     labels: list[str],
                     colormap: dict[str, str],
                     pos: tuple[int, int] = (0, 0),
                     cell: tuple[int, int] = DEFAULT_COLORBAR_CELL,
                     gridcolor: str = core.GRID_COLOR,
                     showgrid: bool = False,
                     showframe: bool = False,
                     default_color: str = '#cccccc'):

    x, y = pos

    hx = x
    hy = y

    for c in labels:
        color = colormap.get(c, default_color)

        svg.add_rect(hx, hy, cell[0], cell[1], fill=color)

        hx += cell[0]

    w = cell[0] * len(labels)
    h = cell[1]

    if showgrid:
        add_grid(svg,
                 pos=pos,
                 size=(w, h),
                 shape=len(labels),
                 color=gridcolor)

    if showframe:
        svg.add_frame(x=x, y=y, w=w, h=h)

    return (w, h)


def add_grid(svg: SVGFigure,
             pos: tuple[int, int] = (0, 0),
             size: tuple[int, int] = (0, 0),
             shape: tuple[int, int] = (0, 0),
             color: str = core.GRID_COLOR,
             stroke: int = core.GRID_STROKE,
             drawrows: bool = True,
             drawcols: bool = True):
    """
    Add grid lines to a figure. Mostly used for enhancing heat maps.

    Args:
        svg (SVGFigure): _description_
        pos (tuple[int, int], optional): _description_. Defaults to (0, 0).
        size (tuple[int, int], optional): _description_. Defaults to (0, 0).
        shape (tuple[int, int], optional): _description_. Defaults to (0, 0).
        color (str, optional): _description_. Defaults to core.GRID_COLOR.
        stroke (int, optional): _description_. Defaults to core.GRID_STROKE.
        drawrows (bool, optional): _description_. Defaults to True.
        drawcols (bool, optional): _description_. Defaults to True.
    """

    x, y = pos
    w, h = size
    rows, cols = shape

    starty = y

    dx = w / cols
    dy = h / rows

    if drawrows:
        #x += dx
        y += dy

        for _ in range(1, rows):
            svg.add_line(x1=x, y1=y, x2=x+w, y2=y,
                         color=color, stroke=stroke)

            y += dy

    if drawcols:
        y = starty
        x += dx

        for _ in range(1, cols):
            svg.add_line(x1=x, y1=y, x2=x, y2=y+h,
                         color=color, stroke=stroke)

            x += dx


def cluster_label_rows(svg: SVGFigure,
                           row_labels,
                           clusters,
                           x=0,
                           y=0,
                           h=0,
                           w=core.LABEL_COLOR_BLOCK_SIZE,
                           padding=5,
                           showgroups=True,
                           frame=True,
                           framecolor='white',
                           stroke=core.STROKE_SIZE,
                           showlabels=True,
                           showblocks=True,
                           mingroupsize=2,
                           weight='normal',
                           invert_x=False,
                           align='left'):
        startx = x
        starty = y

        c = 0

        for group in row_labels:
            c += len(group['items'])

        yd = h / c

        y = 0

        if invert_x:
            x = startx + 30 - w
        else:
            x = startx - 30

        mtw = 0

        c = 0

        for group in row_labels:
            h = yd * len(group['items'])

            for item in group['items']:
                color = clusters.get_color(item)

                if showblocks:
                    svg.add_rect(x, y, w, yd, fill=color)

                    if frame:
                        #svg.add_frame(x, y, w, yd, color=framecolor)

                        if c > 0:
                            svg.add_line(x1=x-padding,
                                          y1=y,
                                          x2=x+w+padding,
                                          y2=y,
                                          color=framecolor,
                                          stroke=stroke)

                if showlabels:
                    tw = svg.get_string_width(item)

                    mtw = max(mtw, tw)

                    if align == 'left':
                        svg.add_text_bb(item,
                                        x=x - tw - 10,
                                        y=y,
                                        h=yd,
                                        color=color)
                    else:
                        svg.add_text_bb(item,
                                        x=x + w + 10,
                                        y=y,
                                        h=yd,
                                        color=color)

                y += yd

                c += 1

        if showgroups:
            y = starty + yd / 2

            for group in row_labels:
                n = len(group['items'])

                x = -mtw - 50
                h = (n - 1) * yd
                color = clusters.get_block_color(group['name'])

                if n > 1:
                    svg.add_line(x,
                                  y - svg.get_font_h() / 2 + padding / 2,
                                  x,
                                  y + h + svg.get_font_h() / 2 - padding / 2,
                                  color=color)

#                svg.add_line(x,
#                              y,
#                              x + core.BRACKET_SIZE,
#                              y,
#                              color=color)
#
#                svg.add_line(x,
#                              y + h,
#                              x + core.BRACKET_SIZE,
#                              y + h,
#                              color=color)

                names = group['name'].split(' ')

                if group['name'] == 'Plasmablasts':
                    names = ['Plasma', 'blasts']

                if n >= mingroupsize:
                    if len(names) == 2:
                        tw = svg.get_string_width(names[0])
                        svg.add_text(names[0], x=x-60, y=y + h / 2 + tw/2, h=yd,
                                      color=color, rotate=-90, weight=weight)
                        tw = svg.get_string_width(names[1])
                        svg.add_text(names[1], x=x-20, y=y + h / 2 + tw/2, h=yd,
                                      color=color, rotate=-90, weight=weight)
                    else:
                        tw = svg.get_string_width(group['name'])
                        svg.add_text(names[0],
                                      x=x-20,
                                      y=y + h / 2 + tw/2,
                                      h=yd,
                                      color=color,
                                      rotate=-90,
                                      weight=weight)

                y += n * yd