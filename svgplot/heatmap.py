#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 09:36:28 2019

@author: antony
"""
import numpy as np
import libplot
import matplotlib
import pandas as pd
import lib10x
from . import svgplot


DEFAULT_CELL = (50, 50)
DEFAULT_COLORBAR_CELL = (50, 25)
DEFAULT_LIMITS = (-2, 2)


def add_heatmap(svg,
                df: pd.DataFrame,
                pos: tuple[int, int] = (0, 0),
                cell: tuple[int, int] = DEFAULT_CELL,
                lim: tuple[int, int] = DEFAULT_LIMITS,
                cmap=libplot.BWR2_CMAP,
                gridcolor=svgplot.GRID_COLOR,
                showgrid: bool = True,
                showframe: bool = True,
                xticklabels: bool = True,
                xticklabel_colors: dict[str, str] = {},
                yticklabels: bool = True,
                row_zscore: bool = False):

    x, y = pos

    if row_zscore:
        df = lib10x.scale(df)

    mapper = matplotlib.cm.ScalarMappable(
        norm=matplotlib.colors.Normalize(vmin=lim[0], vmax=lim[1]), cmap=cmap)

    hx = x
    hy = y

    for i in range(0, df.shape[0]):
        hx = x

        for j in range(0, df.shape[1]):
            v = df.iloc[i, j]
            color = svgplot.rgbatohex(mapper.to_rgba(v))

            svg.add_rect(hx, hy, cell[0], cell[1], fill=color)

            hx += cell[0]

        hy += cell[1]

    w = cell[0] * df.shape[1]
    h = cell[1] * df.shape[0]

    if showgrid:
        add_grid(svg,
                 pos=pos,
                 size=(w, h),
                 shape=df.shape,
                 color=gridcolor)

    if showframe:
        svg.add_frame(x=x, y=y, w=w, h=h)

    if yticklabels:
        y1 = y + cell[1] / 2

        for name in df.index:
            svg.add_text_bb(name, x=w+20, y=y1)
            y1 += cell[1]

    if xticklabels:
        add_xticklabels(svg, df, cell=cell, xticklabel_colors=xticklabel_colors)

    return (w, h)


def add_xticklabels(svg,
                    df: pd.DataFrame,
                    xticklabel_colors: dict[str, str] = {},
                    pos: tuple[int, int] = (0, -30),
                    cell: tuple[int, int] = DEFAULT_CELL):
    """
    Add vertical column labels to heatmap

    Args:
        s
    """
    x, y = pos

    x1 = x + cell[0] / 2

    for name in df.columns:
        color = 'black'

        if len(xticklabel_colors) > 0:
            for label, c in xticklabel_colors.items():
                if label in name:
                    color = c
                    break

        svg.add_text_bb(name, x=x1, y=y, orientation='v', color=color)
        x1 += cell[0]


def add_col_colorbar(svg,
                     labels: list[str],
                     colormap: dict[str, str],
                     pos: tuple[int, int] = (0, 0),
                     cell: tuple[int, int] = DEFAULT_COLORBAR_CELL,
                     gridcolor=svgplot.GRID_COLOR,
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


def add_grid(svg,
             pos: tuple[int, int] = (0, 0),
             size: tuple[int, int] = (0, 0),
             shape: tuple[int, int] = (0, 0),
             color=svgplot.GRID_COLOR,
             stroke=svgplot.GRID_STROKE,
             drawrows=True,
             drawcols=True):
    """
    Add grid lines to a figure. Mostly used for enhancing heat maps.
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
