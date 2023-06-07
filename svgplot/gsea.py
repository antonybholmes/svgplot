import os
import math
import re
from typing import Optional
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from . import core
from . import graph
from .axis import Axis
from .svgfigure import SVGFigure

LINE_GREEN = '#00b359'  # '#90EE90'


class _MidpointNormalize(Normalize):
    def __init__(svg, vmin=None, vmax=None, midpoint=None, clip=False):
        svg.midpoint = midpoint
        Normalize.__init__(svg, vmin, vmax, clip)

    def __call__(svg, value, clip=None):
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        x, y = [svg.vmin, svg.midpoint, svg.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))


def add_gsea(svg: SVGFigure,
             name: str,
             dir: str,
             pos: tuple[float, float] = (0, 0),
             w: int = 400,
             h: Optional[float] = None,
             xoffset: int = 80,
             title: Optional[str] = None,
             showtitle:bool = True,
             phens=None,
             cmap=plt.cm.seismic,
             mode: str = 'up',
             stroke: int = 4,
             scale_factor: float = 0.7,
             n: int = -1,
             weight: str = 'normal',
             titleoffset: int = 20,
             showsnr: bool = True,
             show_gene_indices: bool = True,
             label_pos: str = 'upper right',
             show_y_label: bool = True,
             stat: str = 'q',
             le_fill_opacity: float = 0.3,
             bar_colors = ['red', 'royalblue'],
             label_colors = []):
    """
    Add a gsea plot onto a page. This method adds axes labels to reduce
    scaling effect on fonts.

    Args:
    file: str
        GSEA png plot to insert. It is assumed the plot contains no text
        and has been trimmed to remove whitespace.
    """

    x, y = pos

    # find gene ranking

    for f in os.listdir(dir):
        if 'ranked_gene' in f and 'xls' in f:
            print(f'gene rank: {f}')
            df_gene_ranks = pd.read_csv(f'{dir}/{f}', sep='\t', header=0)

            matcher = re.search('ranked_gene_list_(.+?)_versus_(.+?)_', f)
            if phens is None:
                phens = [matcher.group(1), matcher.group(2)]

            break

    ln = name.lower()

    for f in os.listdir(dir):
        fl = f.lower()
        print(dir, f, name)
        if ln in fl.lower() and 'xls' in f:
            print(f'gene hits: {f}')
            df_hits = pd.read_csv(f'{dir}/{f}', sep='\t', header=0)
            break

    nes_map = {}

    for f in os.listdir(dir):
        if 'gsea_report_for_' in f and 'xls' in f:
            df_rep = pd.read_csv(f'{dir}/{f}', sep='\t', header=0)

            for i in range(df_rep.shape[0]):
                nes_map[df_rep['NAME'][i].lower()] = (
                    df_rep['NES'][i], df_rep['FDR q-val'][i], df_rep['NOM p-val'][i])

    starty = y

    #subtitle = df.iloc[0, 0]
    #subtitle = subtitle.replace('0.000', '0.0')
    #subtitles = subtitle.replace(' ', '').split(',')

    xmax = df_gene_ranks.shape[0]
    xticks = [0, df_gene_ranks.shape[0]]

    ymin = df_hits['RUNNING ES'].min()
    ymax = df_hits['RUNNING ES'].max()

    genes = df_gene_ranks.shape[0]

    xmid = xmax / 2

    if ymax > 0:
        ymax = math.ceil(ymax * 10) / 10
        if ymax < 0.2:
            ymax = 0
    else:
        ymax = math.floor(ymax * 10) / 10

    if ymin > 0:
        ymin = 0
    else:
        ymin = math.floor(ymin * 10) / 10

    hits = df_hits['RANK IN GENE LIST'].values

    zero_cross = df_gene_ranks[df_gene_ranks['SCORE'] > 0].shape[0]

    snr = df_gene_ranks['SCORE'].values

    #norm = _MidpointNormalize(vmin=snr.min(), midpoint=0, vmax=snr.max())
    norm = _MidpointNormalize(vmin=0, midpoint=zero_cross, vmax=xmax)

    plotx = df_hits['RANK IN GENE LIST'].values
    ploty = df_hits['RUNNING ES'].values

    # fix ends

    if plotx[0] != 0:
        plotx = np.insert(plotx, 0, 0)
        ploty = np.insert(ploty, 0, 0)

    if plotx[-1] != genes:
        plotx = np.append(plotx, genes)
        ploty = np.append(ploty, 0)

    df_hits_lead = df_hits[df_hits['CORE ENRICHMENT'] == 'Yes']

    xlead = df_hits_lead['RANK IN GENE LIST'].values
    ylead = df_hits_lead['RUNNING ES'].values

    #  leading edge on left
    if xlead[0] < zero_cross:
        if xlead[0] != 0:
            xlead = np.insert(xlead, 0, 0)
            ylead = np.insert(ylead, 0, 0)

        xlead = np.append(xlead, xlead[-1])
        ylead = np.append(ylead, 0)
    else:
        xlead = np.insert(xlead, 0, xlead[0])
        ylead = np.insert(ylead, 0, 0)

        if xlead[-1] != genes:
            xlead = np.append(xlead, genes)
            ylead = np.append(ylead, 0)

    #ylead[0] = 0
    #ylead[-1] = 0

    # fix for plotting leading edge
    # if xlead[0] < zero_cross:
    #     xlead = np.append(xlead, xlead[-1])
    # else:
    #     xlead = np.append(xlead, xlead[0])

    # ylead = np.append(ylead, 0)

    #heatmap = file.replace('gsea_plot', 'heat_map').replace('params.txt', 'png')

    if w is None or h is None:
        if w is None:
            w = h / 0.85
        else:
            h = scale_factor * w

    if showtitle:
        if title is None:
            title = name

        if n == -1:
            n = genes

        title = f'{title} (n={n:,})'
        svg.add_text_bb(title, x=x+xoffset+w/2,
                        y=y,
                        w=w,
                        align='c',
                        weight=weight)
        y += svg.get_font_h() + titleoffset  # 0.5 * padding

    scaleh = scale_factor * h

    xaxis = Axis(lim=[0, xmax], w=w)
    yaxis = Axis(lim=[ymin, ymax], w=scaleh,
                 label='Enrichment' if show_y_label else '')

    # leading edge
    points = [[xoffset + xaxis.scale(px), y + scaleh - yaxis.scale(py)]
              for px, py in zip(xlead, ylead)]
    svg.add_polyline(points, color='none',
                     fill=LINE_GREEN, stroke=stroke, fill_opacity=le_fill_opacity)

    # scale points
    points = [[xoffset + xaxis.scale(px), y + scaleh - yaxis.scale(py)]
              for px, py in zip(plotx, ploty)]

    # python light green as html
    svg.add_polyline(points, color=LINE_GREEN, stroke=stroke)

    #hw, hh, hi = svg.base_image(heatmap, w=w, h=h*0.06)

    #print(hi, hw, hh)

    #
    # subtitles
    #

    # if smallfont:
    #     svg.set_font_size(core.FIGURE_FONT_SIZE)
    # else:
    #     svg.set_font_size(core.DEFAULT_FONT_SIZE)

    #svg.add_text_bb(subtitle, x=x+xoffset, y=y, w=w, align='c')
    #y += svg.get_font_h()
    #svg.add_trans(hi, x=x+xoffset, y=y+h-hh)

    # if float(subtitles[1].split('=')[1]) < 0.05:
    #     pcolor = 'black'
    # else:
    #     pcolor = 'gray'

    # if subtitle_pos == 'upper right':
    #     svg.add_text(subtitles[0],
    #                   x=x+w-60,
    #                   y=y+svg.get_font_h(),
    #                   color=pcolor)
    #     svg.add_text(subtitles[1],
    #                   x=x+w-60,
    #                   y=y + 2 * svg.get_font_h() + padding,
    #                   color=pcolor)
    # elif subtitle_pos == 'lower left':
    #     svg.add_text(subtitles[0],
    #                   x=x + xoffset + padding,
    #                   y=y + scaleh - 1.5 * svg.get_font_h() - padding,
    #                   color=pcolor)
    #     svg.add_text(subtitles[1],
    #                   x=x + xoffset + padding,
    #                   y=y + scaleh - svg.get_font_h() / 2,
    #                   color=pcolor)
    # else:
    #     pass

    # label axes

    # yaxis
    # if smallfont:
    #     svg.set_font_size(core.FIGURE_FONT_SIZE)

    #ticks = [ymin, round((((ymax+ymin) / 2) * 10) / 10, 1), ymax]
    ticks = [ymin, ymax]

    if ymin == 0:
        ticks = [ymin, ymax]
    elif ymax == 0:
        ticks = [ymin, ymax]
    else:
        ticks = [ymin, 0, ymax]

    # if ymax > 0:
    #     ticks[2] = round(2 * ticks[1] - ticks[0], 1)
    # else:
    #     ticks[0] = round(2 * ticks[1] - ticks[2], 1)

    print(ymin, ymax, ticks)

    graph.add_y_axis(svg,
                     pos=(xoffset, y),
                     axis=yaxis,
                     ticks=ticks,
                     padding=core.TICK_SIZE,
                     showticks=True,
                     stroke=stroke)

    # draw line at y =0

    y1 = y + scaleh - yaxis.scale(0)  # (0 - ymin) / (ymax - ymin) * scaleh

    svg.add_line(x1=xoffset, y1=y1, x2=xoffset+w, y2=y1, stroke=stroke)

    # add labels

    print('nes_map', ln, nes_map)
    if ln in nes_map:
        if label_pos == 'upper right':
            x1 = w - 100
            svg.add_text_bb(f'NES: {nes_map[ln][0]:.2f}', x=x1, y=y)

            if stat == 'q':
                svg.add_text_bb(f'q: {nes_map[ln][1]:.2f}', x=x1, y=y+35)
            else:
                svg.add_text_bb(f'p: {nes_map[ln][2]:.2f}', x=x1, y=y+35)
        else:
            x1 = 90
            svg.add_text_bb(f'NES: {nes_map[ln][0]:.2f}', x=x1, y=scaleh-60)

            if stat == 'q':
                svg.add_text_bb(
                    f'q: {nes_map[ln][1]:.2f}', x=x1, y=scaleh-25)
            else:
                svg.add_text_bb(
                    f'p: {nes_map[ln][2]:.2f}', x=x1, y=scaleh-25)

    #
    # draw hits
    #
    y += scaleh + 10
    sh = h * 0.10

    for hit in hits:
        x1 = xoffset + xaxis.scale(hit)  # hit / xmax * w

        if hit <= zero_cross:  # xmid:
            color = bar_colors[0]
        else:
            color = bar_colors[1]

        svg.add_line(x1=x1, y1=y, x2=x1, y2=y+sh, color=color)

    # add frame around colorbar
    #svg.add_frame(xoffset, y=y-h*0.06, w=w, h=h*0.06)

    #
    # heat bar
    #
    # col = core.rgbtohex(cmap(int(norm(snr[0]) * cmap.N - 1)))

    # svg.add_rect(x=xoffset, y=y-25, w=w, h=20, fill=col)

    # for hit in hits:
    #     v = snr[hit]
    #     x1 = xaxis.scale(hit)
    #     w1 = w - x1
    #     col = core.rgbtohex(cmap(int(norm(v) * cmap.N - 1)))
    #     svg.add_rect(x=xoffset+x1, y=y-25, w=w1, h=20, fill=col)

    # svg.add_frame(xoffset, y=y-25, w=w, h=20)

    # svg.add_svg_colorbar(
    #          x=xoffset,
    #          y=y-25,
    #          w=w,
    #          h=20,
    #          steps=hits,
    #          cmap=cmap.reversed(), #matplotlib.cm.viridis,
    #          xaxis=xaxis,
    #          norm=norm,
    #          showaxis=False)

    # svg.add_svg_colorbar(
    #          x=xoffset+800,
    #          y=y,
    #          w=w,
    #          h=20)

    #
    # Labels
    #

    # if smallfont:
    #     svg.set_font_size(core.FIGURE_FONT_SIZE)
    # else:
    #     svg.set_font_size(core.DEFAULT_FONT_SIZE)

    y += sh + svg.get_font_h()

    if isinstance(phens, list) or isinstance(phens, tuple):
        #y += svg.get_font_h() - 5

        svg.add_text_bb(phens[0], x=xoffset, y=y, color=label_colors[0] if len(label_colors) > 0 else bar_colors[0])
        svg.add_text_bb(phens[1], x=xoffset + w, y=y,
                        align='r', color=label_colors[1] if len(label_colors) > 0 else bar_colors[1])
    # else:
    #     svg.add_line(x1=xoffset, y1=y, x2=xoffset, y2=y+padding)

    #     xp = xoffset + xtick / xmax * w  # (w - 2 * xoffset)

    #     svg.add_line(x1=xp, y1=y, x2=xp, y2=y+padding)

    #     mid = math.floor(xtick / 2 / 10000) * 10000

    #     xp2 = xoffset + xaxis.scale(mid)  # (w - 2 * xoffset)

    #     svg.add_line(x1=xp2, y1=y, x2=xp2, y2=y+padding)

    #     y += svg.get_font_h() + padding

    #     svg.add_text_bb('0', x=xoffset, y=y, align='c')
    #     svg.add_text_bb(str(mid), x=xp2, y=y, align='c')
    #     svg.add_text_bb(str(xtick), x=xp, y=y, align='c')

    y += 30

    #
    # Draw snr
    #

    if showsnr:

        m = round(int(max(abs(snr)) * 10) / 10, 1)
        ymin = -m
        ymax = m
        scaleh = h * 0.3
        yaxis = Axis(lim=[ymin, ymax], w=scaleh, label='SNR')

        svg.add_y_axis(x=xoffset,
                       y=y,
                       axis=yaxis,
                       ticks=[-m, 0, m],
                       padding=core.TICK_SIZE,
                       showticks=True,
                       stroke=stroke)

        # gray
        points = [[xoffset + xaxis.scale(0), y + scaleh - yaxis.scale(0)]]
        points.extend([[xoffset + xaxis.scale(px), y + scaleh - yaxis.scale(py)]
                      for px, py in zip(range(0, xmax), snr)])
        points.extend(
            [[xoffset + xaxis.scale(xmax), y + scaleh - yaxis.scale(0)]])
        svg.add_polyline(points, color='none',
                         fill='#4d4d4d', stroke=stroke, fill_opacity=0.3)

        x1 = xoffset + xaxis.scale(zero_cross)
        svg.add_line(x1=x1, y2=y+scaleh-yaxis.scale(ymax), x2=x1,
                     y1=y+scaleh-yaxis.scale(ymin), stroke=stroke, dashed=True)

        # draw line at y =0
        y1 = y + scaleh - yaxis.scale(0)
        #svg.add_line(x1=xoffset, y1=y1, x2=xoffset+w, y2=y1, stroke=core.AXIS_STROKE)

        y += scaleh + 40

    if show_gene_indices:
        svg.add_text_bb(str(0), x=xoffset, y=y, align='c')
        svg.add_text_bb(f'{genes:,}', x=xoffset+w, y=y, align='c')

    return w + xoffset, y - starty + 2 * svg.get_font_h()
