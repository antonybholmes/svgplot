#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 09:36:28 2019

@author: antony
"""
from typing import Optional, Union
import numpy as np
import libplot
import matplotlib
import pandas as pd
from . import svgplot
from .svgfigure import SVGFigure
from .axis import Axis
from scipy.stats import zscore


def dot_plot(svg: SVGFigure,
             df_data: pd.DataFrame,
             df_coldata: pd.DataFrame,
             genes: list[str],
             groups: list[str] = [],
             groupby: str = 'Phenotype',
             use_zscore: bool = True,
             cmap=libplot.BWR2_CMAP,
             vlim: tuple[float, float] = (-0.5, 0.5),
             min_exp: int = 0,
             fraction_groups: list[float]=[0.25, 0.5, 0.75, 1],
             dot_sizes: tuple[int, int] = (8, 26),
             pos: tuple[int, int] = (0, 0),
             gap: tuple[int, int] = (40, 28),
             title_offset: int = 40,
             linecolor: str = 'black',
             show_row_labels: bool = False,
             show_col_labels: bool = False,
             label_colors: dict[str, str] = {},
             row_color: str = "black",
             frac_file: str = "fractions.txt",
             stroke: int = svgplot.STROKE_SIZE,
             showframe: bool = True,
             frac_filter={},
             mode: str = 'exp',
             df_exp: Optional[pd.DataFrame] = None):
    """
    Generate a dot plot

    Args:
        svg (SVGFigure): _description_
        df_data (pd.DataFrame): _description_
        df_coldata (pd.DataFrame): _description_
        genes (list[str]): _description_
        groups (list[str], optional): _description_. Defaults to [].
        groupby (str, optional): _description_. Defaults to 'Phenotype'.
        use_zscore (bool, optional): _description_. Defaults to True.
        cmap (_type_, optional): _description_. Defaults to libplot.BWR2_CMAP.
        vlim (tuple[float, float], optional): _description_. Defaults to (-0.5, 0.5).
        min_exp (int, optional): _description_. Defaults to 0.
        fraction_groups (list[float], optional): _description_. Defaults to [0.25, 0.5, 0.75, 1].
        dot_sizes (tuple[int, int], optional): _description_. Defaults to (8, 26).
        pos (tuple[int, int], optional): _description_. Defaults to (0, 0).
        gap (tuple[int, int], optional): _description_. Defaults to (40, 28).
        title_offset (int, optional): _description_. Defaults to 40.
        linecolor (str, optional): _description_. Defaults to 'black'.
        show_row_labels (bool, optional): _description_. Defaults to False.
        show_col_labels (bool, optional): _description_. Defaults to False.
        label_colors (dict[str, str], optional): _description_. Defaults to {}.
        row_color (str, optional): _description_. Defaults to "black".
        frac_file (str, optional): _description_. Defaults to "fractions.txt".
        stroke (int, optional): _description_. Defaults to svgplot.STROKE_SIZE.
        showframe (bool, optional): _description_. Defaults to True.
        frac_filter (dict, optional): _description_. Defaults to {}.
        mode (str, optional): _description_. Defaults to 'exp'.
        df_exp (Optional[pd.DataFrame], optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """

    x, y = pos

    if len(frac_filter) == 0:
        frac_filter = {g: 0 for g in groups}

    data_mode = 'as.is'

    if df_exp is None:
        data_mode = 'calc'
        df_exp = df_data.copy()

    if not isinstance(groups[0], dict):
        groups = [{'name': 'All', 'items': groups}]

    genes = np.array(genes)

    ncols = np.sum([len(g['items']) for g in groups])

    # df_exp = df_exp.iloc[np.where(df_exp.sum(axis=1) > 0)[0], :]

    idx = []

    for g in genes:
        i = np.where(df_data.index == g)[0]

        if i.size > 0:
            i = i[0]
            idx.append(i)
        else:
            # print('ugh', g, i)
            pass

    df_data = df_data.iloc[idx, :]

    # make sure in same order
    idx = np.array([np.where(df_exp.index == g)[0][0]
                   for g in df_data.index])
    df_exp = df_exp.iloc[idx, :]

    df_group_exp_avg = np.zeros((df_data.shape[0], ncols))

    i = 0
    colnames = []

    for group in groups:
        for g in group['items']:
            colnames.append(g)

            if data_mode == 'as.is':
                idx = np.where(df_data.columns == g)[0][0]
                m = df_data.iloc[:, idx].values
            else:
                idx = np.where(df_coldata[groupby] == g)[0]
                t = df_exp.iloc[:, idx]
                m = t.mean(axis=1)

            df_group_exp_avg[:, i] = m
            i += 1

    colnames = np.array(colnames)

    z_group = zscore(df_group_exp_avg, axis=1)
    df_z_group = pd.DataFrame(z_group, index=df_exp.index, columns=colnames)

    # z = zscore(df_exp, axis=1)
    # df_z = pd.DataFrame(z, index=df_exp.index, columns=df_exp.columns)

    # custom z score based on klein, califano 2003 transcriptional analysis
    m = 0
    sd = 0
    for g in colnames:
        if data_mode == 'as.is':
            idx = np.where(df_data.columns == g)[0][0]
            m += df_data.iloc[:, idx].values
            sd += df_data.iloc[:, idx].values
        else:
            idx = np.where(df_coldata[groupby] == g)[0]
            t = df_exp.iloc[:, idx].values
            m += np.mean(t, axis=1)
            sd += np.std(t, axis=1)

    m /= colnames.size
    sd /= colnames.size

    z = df_data.subtract(m, axis=0).divide(sd, axis=0)
    df_z = pd.DataFrame(z, index=df_data.index, columns=df_data.columns)

    tables = {}
    fractions = {}

    c = 0
    for group in groups:
        for g in group['items']:
            idx = np.where(df_coldata[groupby] == g)[0]

            t = df_exp.iloc[:, idx]
            m = np.zeros(t.shape, dtype=int)
            m[t > min_exp] = 1
            f = np.sum(m, axis=1) / m.shape[1]
            fractions[g] = f

            if data_mode == 'as.is':
                idx = np.where(df_data.columns == g)[0][0]
                t = df_data.iloc[:, idx].values

            if use_zscore:
                if mode == 'group':
                    tables[g] = df_z_group.iloc[:, c]
                else:
                    tables[g] = np.mean(df_z.iloc[:, idx].values, axis=1)

            else:
                tables[g] = t

            c += 1

    #
    # filter fractions
    #

    idx = np.array([], dtype=int)  # range(0, df_data.shape[0]))

    print('filter 1', idx.size)

    for g in frac_filter:
        if g in fractions:
            print(g, fractions[g], fractions[g].size)
            idx = np.union1d(idx, np.where(fractions[g] >= frac_filter[g]))

    idx = np.sort(idx)

    df_data = df_data.iloc[idx, :]
    df_exp = df_exp.iloc[idx, :]

    for g in fractions:
        fractions[g] = fractions[g][idx]

    for g in tables:
        tables[g] = tables[g][idx]

    norm = matplotlib.colors.Normalize(vmin=vlim[0], vmax=vlim[1])

    # sort

    fracs = fractions[colnames[0]]
    m = np.array([norm(x) for x in tables[colnames[0]]])

    s = 2 * m + fracs

    idx = np.argsort(s)[::-1]

    # df_data = df_data.iloc[idx, :]
    # df_exp = df_exp.iloc[idx, :]

    # for g in fractions:
    #     fractions[g] = fractions[g][idx]

    # for g in tables:
    #     tables[g] = tables[g][idx]

    mapper = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)

    dot_range = dot_sizes[1] - dot_sizes[0]

    x1 = x

    # group_index = 0

    for group in groups:
        for g in group['items']:
            y1 = y

            m = tables[g]
            fracs = fractions[g]
            # m = t.mean(axis=1)

            if show_col_labels:
                if g in label_colors:
                    color = label_colors[g]
                else:
                    color = 'black'

                svg.add_text_bb(g, x1, y1 - title_offset,
                                orientation='v', color=color)

            for gene_index in range(0, m.size):
                # gene = t.index[gene_index]

                v = m[gene_index]

                print(g, gene_index, v)

                # if use_zscore:
                #    v = df_z.iloc[gene_index, group_index]
                # else:
                #    v = df_group_exp_avg[gene_index, group_index]

                # use mean for color
                # m[gene_index]))
                color = svgplot.rgbatohex(mapper.to_rgba(v))

                dot_size = max(
                    dot_sizes[0], fracs[gene_index] * dot_sizes[1])

                svg.add_circle(x1, y1, dot_size,
                               fill=color, color=linecolor, stroke=stroke)

                # if group_index == ncols - 1 and show_row_labels:
                #    svg.add_text_bb(gene, x1+label_offset,
                #                     y1, color=row_color)

                y1 += gap[1]

            x1 += gap[0]

            # group_index += 1

        # add some separation between groups
        x1 += gap[0] / 2

    n = df_data.shape[0] - 1  # tables[0].shape[0] - 1
    # reverse labels as axis draw opposite to rendering direction
    yaxis = Axis(lim=[0, n], ticklabels=np.array(
        list(reversed(df_data.index.values))), w=n*gap[1])

    # plot gene names from Table 0 as all tables are the same
    if show_row_labels:
        svg.add_y_axis(x=x1-gap[0],
                       y=y+yaxis.w,
                       axis=yaxis,
                       showline=not showframe,
                       side='r',
                       tickcolor=row_color)

    # if showframe:
    #    svg.add_rect(x=x-gap[0], y=y-gap[0], w=x1, h=yaxis.w+gap[0], color='black', stroke=svgplot.AXIS_STROKE)

        # for gene in tables[0].index:
        #    svg.add_text_bb(gene, x1+label_offset, y1, color=row_color)
        #    y1 += gap[1]

    y1 += 50

    x1 = x

    if len(fraction_groups) > 0:
        for f in fraction_groups:
            dot_size = max(dot_sizes[0], f * dot_sizes[1])
            svg.add_circle(x1, y1, dot_size, fill='gray', color=linecolor)
            svg.add_text_bb(str(int(f * 100)), x1,
                            y1+title_offset, align='c')
            x1 += 50

        x1 += 50

        # svg.add_num_colorbar_z(x=x1, y=y1, name='bwr2', z=1, align='l')

        # svg.add_svg_colorbar(x=x1, y=y1, cmap=libplot.BWR2_CMAP, ticks=[0, 0.5, 1], ticklabels=[vlim[0], 0.0, vlim[1]], align='l')

    # svg.set_font_size(svgplot.DEFAULT_FONT_SIZE)

    tables = []
    for group in groups:
        df_frac = pd.DataFrame(index=df_data.index)
        for c in colnames:
            df_frac[c] = fractions[c]

        print(df_frac)

        # print(colnames, np.concatenate([fractions[g] for g in colnames]))
        # df_frac = pd.DataFrame(np.concatenate([fractions[g] for g in colnames], axis=1), index=genes, columns = colnames)
        df_frac *= 100
        tables.append(df_frac)

    df_frac = pd.concat(tables, axis=1)
    df_frac.round(2).to_csv(frac_file, sep='\t', header=True, index=True)

    return df_exp


def dot_plot_legend(svg: SVGFigure,
                    pos: tuple[int, int] = (0, 0),
                    fraction_groups: list[float] = [0.25, 0.5, 0.75, 1],
                    dot_sizes: tuple[int, int] = (8, 30),
                    linecolor: str = 'black'):

    x, y = pos

    x1 = x

    for f in fraction_groups:
        dot_size = max(dot_sizes[0], f * dot_sizes[1])
        svg.add_circle(x1, y, dot_size, fill='gray', color=linecolor)
        svg.add_text_bb('{}%'.format(int(f * 100)), x1,
                        y+dot_sizes[1]+10, align='c')
        x1 += 70

    # svg.set_font_size(svgplot.DEFAULT_FONT_SIZE)
