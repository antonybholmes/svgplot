import numpy as np
from . import core
from .axis import Axis
from .svgfigure import SVGFigure
from .svgfiguremod import SVGFigureModule
from . import graph
from . import matrix
import re

SIG = -np.log10(0.05)
SUB_TYPE_COLORS = {'MCD': 'blue', 'BN2': 'fuchsia', 'N1': 'limegreen', 'EZB': 'chocolate', 'A53': 'black',  'ST2': 'red', 'Other': 'gray', 'Composite': 'cornflowerblue'}


def add_enrichment_plot(svg,
                        df_coo,
                        clusters,
                        row_labels,
                        pos=(0, 0),
                        w=300,
                        bar_width=8,
                        bar_gap=0,
                        block_gap=5,
                        block_gap_t=-1,
                        block_gap_b=-1,
                        xlim=[0, 12],
                        xticks=[0, 4, 8, 12],
                        xminorticks=range(2, 12, 2),
                        sigq=0.05,
                        showxaxis=True,
                        showlabels=True,
                        showblocks=True,
                        colormap=core.ABC_COLORS,
                        frame=False,
                        framecolor='black',
                        stroke=core.STROKE_SIZE,
                        sigqcolor='#ffffff',
                        invert_x=False,
                        xlabel='-log10(q)'):
    # if smallfont:
    #    svg.set_font_size(core.FIGURE_FONT_SIZE)

    x, y = pos

    if block_gap_t == -1:
        block_gap_t = block_gap

    if block_gap_b == -1:
        block_gap_b = block_gap

    # shift by a small amount to get rid of zero problem
    df_coo = -np.log10(df_coo.round(10) + 0.00000000001)

    bar_block = (bar_width * df_coo.shape[1]) + (bar_gap *
                                                 (df_coo.shape[1] - 1)) + (block_gap_t + block_gap_b)

    n = np.sum([len(row_block['items']) for row_block in row_labels])

    h = n * bar_block

    xaxis = Axis(lim=xlim, w=w)

    y2 = y  # - yaxis.scale(yaxis.lim[1] - 0.5)

    yd = h / n

    # gray out section

    if sigq > 0:
        if invert_x:
            x2 = x - xaxis.scale(-np.log10(sigq))
        else:
            x2 = x + xaxis.scale(-np.log10(sigq))

        #svg.add_rect(x, y2, x2-x, h, fill=sigqcolor)
        svg.add_line(x1=x2, y1=y2+h, x2=x2, y2=y2, dashed=True)

    # draw bars

    ids = []

    for name in df_coo.index:
        if str(name) == 'nan':
            continue

        if isinstance(name, str):
            matcher = re.search(r'(\d+)', name)

            if matcher:
                ids.append(clusters.find(int(matcher.group(1))))
            else:
                ids.append(name)
        else:
            print(name)
            ids.append(clusters.find(name))

    ids = np.array(ids)

    for row_block in row_labels:
        for label in row_block['items']:
            label = label.replace('PreM 1', 'PreM')

            i = np.where(ids == label)[0]

            if i.size > 0:
                i = i[0]
            else:
                i = -1

            y3 = y2 + block_gap_t

            for j in range(df_coo.shape[1]):
                col = df_coo.columns[j]

                col = col.replace(' q', '')  # col.split(' ')[0]

                color = colormap[col]

                if isinstance(color, tuple):
                    color = core.rgbtohex(color)

                v = df_coo.iloc[i, j]

                w = xaxis.scale(v)

                if invert_x:
                    x1 = x - w
                else:
                    x1 = x

                svg.add_rect(x1, y3, w=w, h=bar_width, fill=color)

                if frame:
                    w2 = xaxis.scale(v)
                    #svg.add_frame(x, y3, w=w2, h=bar_width)

                    svg.add_line(x1=x, y1=y3, x2=x+w2+stroke /
                                 2, y2=y3, stroke=stroke)
                    svg.add_line(x1=x, y1=y3+bar_width, x2=x+w2 +
                                 stroke/2, y2=y3+bar_width, stroke=stroke)
                    svg.add_line(x1=x+w2, y1=y3, x2=x+w2,
                                 y2=y3+bar_width, stroke=stroke)

                y3 += bar_width + bar_gap

            y2 += yd

    svg.add_line(x1=0, y1=y, x2=0, y2=y2, stroke=core.AXIS_STROKE)

    if showxaxis:
        graph.add_x_axis(svg,
                         axis=xaxis,
                         pos=(0,y2),
                         ticks=xticks,
                         minorticks=xminorticks,
                         label=xlabel,
                         invert=invert_x)

    # svg.set_font_size(core.DEFAULT_FONT_SIZE)

    matrix.cluster_label_rows(svg, row_labels,
                           clusters,
                           h=h,
                           showgroups=False,
                           showblocks=showblocks,
                           showlabels=showlabels,
                           invert_x=invert_x)

    return xaxis.w, h


def add_hits_plot(svg,
                  df_coo,
                  clusters,
                  row_labels,
                  x=0,
                  y=0,
                  h=300,
                  bar_width=30,
                  bar_gap=10,
                  block_gap=20,
                  bar_color='#cccccc',
                  ylim=[0, 30],
                  yticks=[0, 10, 20, 30],
                  padding=10,
                  whisker_size=20,
                  tick_size=core.TICK_SIZE,
                  sigq=0.05,
                  showyaxis=True,
                  showlabels=True,
                  colormap=core.ABC_COLORS,
                  smallfont=False,
                  frame=False,
                  stroke=core.STROKE_SIZE):
    # if smallfont:
    #    svg.set_font_size(core.FIGURE_FONT_SIZE)

    classes = np.array(list(sorted(set(df_coo['Classification'].values))))

    bar_block = (bar_width * classes.size) + \
        (bar_gap * (classes.size - 1)) + (2 * block_gap)

    w = df_coo.shape[0] // 2 * bar_block

    yaxis = Axis(lim=ylim, w=h)

    y2 = y + h

    x2 = x  # - yaxis.scale(yaxis.lim[1] - 0.5)

    xd = w / (df_coo.shape[0] // 2)

    # gray out section

    # draw bars

    ids = []

    for id in df_coo['Id']:
        if id not in ids:
            ids.append(id)

    ids = np.array([clusters.find(id) for id in ids])

    for row_block in row_labels:
        for label in row_block['items']:
            label = label.replace('PreM 1', 'PreM')
            idx = np.where(df_coo['Cluster'] == label)[0]

            x3 = x2 + block_gap

            for j in range(0, idx.size):
                col = df_coo['Classification'][idx[j]]

                color = colormap[col]

                if isinstance(color, tuple):
                    color = core.rgbtohex(color)

                v = df_coo['% Class'][idx[j]]

                sig = df_coo['-log10(q)'][idx[j]] > SIG

                y3 = y2 - yaxis.scale(v)

                svg.add_rect(x3, y3, w=bar_width, h=yaxis.scale(v), fill=color)

                if frame and y2 - y3 > 2:
                    svg.add_line(x1=x3,
                                 y1=y3-stroke/2,
                                 x2=x3,
                                 y2=y2,
                                 stroke=stroke)

                    svg.add_line(x1=x3+bar_width,
                                 y1=y3-stroke/2,
                                 x2=x3+bar_width,
                                 y2=y2,
                                 stroke=stroke)

                    svg.add_line(x1=x3,
                                 y1=y3,
                                 x2=x3+bar_width,
                                 y2=y3,
                                 stroke=stroke)

                if sig:
                    # svg.set_font_size(core.HEADING_FONT_SIZE)
                    svg.add_text_bb('*',
                                    x=x3,
                                    w=bar_width,
                                    y=y2 - yaxis.scale(v) -
                                    svg.get_font_h() / 2,
                                    align='c')

                    # svg.set_font_size(core.DEFAULT_FONT_SIZE)

                x3 += bar_width + bar_gap

            x2 += xd

        # For testing
        #svg.add_line(x1=x, y1=y2, x2=x+100, y2=y2)

    svg.add_line(x1=0, y1=y2, x2=w, y2=y2, stroke=core.AXIS_STROKE)

    if showyaxis:
        svg.add_y_axis(axis=yaxis, y=y2, ticks=yticks, label='% Class')

    # svg.set_font_size(core.DEFAULT_FONT_SIZE)

    if showlabels:
        svg.cluster_label_cols(row_labels, clusters,
                               y=y2, w=w, showgroups=False)

    return w, yaxis.w


def add_enrich_dep_plot(svg,
                        tables,
                        clusters,
                        cluster_groups,
                        x=0,
                        y=0,
                        height=300,
                        bar_width=8,
                        bar_gap=0,
                        block_gap=[5, 5],
                        bar_color='#cccccc',
                        bar_border='black',
                        ylim=[0, 16],
                        yticks=[0, 4, 8, 12, 16],
                        yticklabels=['', '4', '8', '12', '16'],
                        yminorticks=[],
                        padding=10,
                        whisker_size=20,
                        tick_size=core.TICK_SIZE,
                        sigq=0.05,
                        showyaxis=True,
                        showlabels=True,
                        showblocks=True,
                        colormap=core.ABC_COLORS,
                        smallfont=False,
                        frame=False,
                        framecolor='black',
                        stroke=core.STROKE_SIZE,
                        sigqcolor='#ffffff',
                        cluster_group_gap=50):
    # if smallfont:
    #    svg.set_font_size(core.FIGURE_FONT_SIZE)

    # enrich

    yaxis = Axis(lim=ylim, w=height)

    df_coo = np.round(-np.log10(tables[0] + 1E-16), 16)

    bar_block = (bar_width * df_coo.shape[1]) + (bar_gap *
                                                 (df_coo.shape[1] - 1)) + (block_gap[0] + block_gap[1])

    n = np.sum([len(row_block['items']) for row_block in cluster_groups])

    w = n * bar_block

    x2 = x + cluster_group_gap/2  # - yaxis.scale(yaxis.lim[1] - 0.5)

    # gray out section

    if sigq > 0:
        y2 = y - yaxis.scale(-np.log10(sigq))

    # draw bars

    ids = []

    for name in df_coo.index:
        if str(name) == 'nan':
            continue

        if name == 101:
            continue

        if isinstance(name, str):
            matcher = re.search(r'(\d+)', name)

            if matcher:
                ids.append(clusters.find(int(matcher.group(1))))
            else:
                ids.append(name)
        else:
            ids.append(clusters.find(name))

    ids = np.array(ids)

    x1 = x2
    bx = x2

    for row_block in cluster_groups:
        for label in row_block['items']:
            if label == 'PreM-1':
                label = 'PreM'

            i = np.where(ids == label)[0]

            if i.size > 0:
                i = i[0]
            else:
                i = -1

            for j in range(df_coo.shape[1]):
                col = df_coo.columns[j]

                # col = col.split(' ')[0] #col.replace(' q', '') #col.split(' ')[0]

                color = colormap[col]

                if isinstance(color, tuple):
                    color = core.rgbtohex(color)

                v = df_coo.iloc[i, j]

                h = yaxis.scale(v)

                y1 = y - h

                svg.add_rect(x2, y1, w=bar_width, h=h,
                             fill=color, stroke=stroke)

                # if frame:
                #     w2 = xaxis.scale(v)
                #     #svg.add_frame(x, y3, w=w2, h=bar_width)

                #     svg.add_line(x1=x, y1=y3, x2=x+w2+stroke/2, y2=y3, stroke=stroke)
                #     svg.add_line(x1=x, y1=y3+bar_width, x2=x+w2+stroke/2, y2=y3+bar_width, stroke=stroke)
                #     svg.add_line(x1=x+w2, y1=y3, x2=x+w2, y2=y3+bar_width, stroke=stroke)

                x2 += bar_width + bar_gap

            if bar_border is not None:
                svg.add_rect(x=bx, y=y-height, w=bar_width *
                             df_coo.shape[1], h=height, color=bar_border, stroke=stroke)

            bx = x2

            # break
        svg.add_line(x1=x1, y1=y, x2=x2, y2=y, stroke=core.AXIS_STROKE)
        svg.add_line(x1=x1, y1=y2, x2=x2, y2=y2,
                     dashed=True, stroke=core.AXIS_STROKE)
        x2 += cluster_group_gap
        x1 = x2
        bx = x2

    # dashed line
    #svg.add_rect(x, y2, x2-x, h, fill=sigqcolor)
    #svg.add_line(x1=x, y1=y2, x2=x2, y2=y2, dashed=True)

    #svg.add_line(x1=x, y1=y, x2=x2, y2=y, stroke=core.AXIS_STROKE)

    if showyaxis:
        yticklabels1 = yticklabels.copy()
        yticklabels1[0] = '0'
        svg.add_y_axis(axis=yaxis,
                       x=x,
                       y=y,
                       ticks=yticks,
                       ticklabels=yticklabels1,
                       minorticks=yminorticks,
                       label='-log10(q)',
                       title_offset=90)

    svg.add_text_bb('Enrichment', x=x2-20, y=y-height/2,
                    size=core.FIGURE_FONT_SIZE, orientation='v', align='c')

    # dep

    y += 10

    df_coo = np.round(-np.log10(tables[1] + 1E-16), 16)

    bar_block = (bar_width * df_coo.shape[1]) + (bar_gap *
                                                 (df_coo.shape[1] - 1)) + (block_gap[0] + block_gap[1])

    n = np.sum([len(row_block['items']) for row_block in cluster_groups])

    w = n * bar_block

    x2 = x + cluster_group_gap/2  # - yaxis.scale(yaxis.lim[1] - 0.5)

    # gray out section

    if sigq > 0:
        y2 = y + yaxis.scale(-np.log10(sigq))

    # draw bars

    ids = []

    for name in df_coo.index:
        if str(name) == 'nan':
            continue

        if name == 101:
            continue

        if isinstance(name, str):
            matcher = re.search(r'(\d+)', name)

            if matcher:
                ids.append(clusters.find(int(matcher.group(1))))
            else:
                ids.append(name)
        else:
            ids.append(clusters.find(name))

    ids = np.array(ids)

    x1 = x2
    bx = x2

    for row_block in cluster_groups:

        for label in row_block['items']:
            if label == 'PreM-1':
                label = 'PreM'

            i = np.where(ids == label)[0]

            if i.size > 0:
                i = i[0]
            else:
                i = -1

            for j in range(df_coo.shape[1]):
                col = df_coo.columns[j]

                # col = col.split(' ')[0] #col.replace(' q', '') #col.split(' ')[0]

                color = colormap[col]

                if isinstance(color, tuple):
                    color = core.rgbtohex(color)

                v = df_coo.iloc[i, j]

                h = yaxis.scale(v)

                y1 = y + h

                svg.add_rect(x2, y, w=bar_width, h=h, fill=color)

                # if frame:
                #     w2 = xaxis.scale(v)
                #     #svg.add_frame(x, y3, w=w2, h=bar_width)

                #     svg.add_line(x1=x, y1=y3, x2=x+w2+stroke/2, y2=y3, stroke=stroke)
                #     svg.add_line(x1=x, y1=y3+bar_width, x2=x+w2+stroke/2, y2=y3+bar_width, stroke=stroke)
                #     svg.add_line(x1=x+w2, y1=y3, x2=x+w2, y2=y3+bar_width, stroke=stroke)

                x2 += bar_width + bar_gap

            if bar_border is not None:
                svg.add_rect(x=bx, y=y, w=bar_width *
                             df_coo.shape[1], h=height, color=bar_border)

            bx = x2

            # break
        svg.add_line(x1=x1, y1=y, x2=x2, y2=y, stroke=core.AXIS_STROKE)
        svg.add_line(x1=x1, y1=y2, x2=x2, y2=y2, dashed=True)
        x2 += cluster_group_gap
        x1 = x2
        bx = x2

    # dashed line
    #svg.add_rect(x, y2, x2-x, h, fill=sigqcolor)
    #svg.add_line(x1=x, y1=y2, x2=x2, y2=y2, dashed=True)
    #svg.add_line(x1=x, y1=y, x2=x2, y2=y, stroke=core.AXIS_STROKE)

    if showyaxis:
        graph.add_y_axis(svg, axis=yaxis,
                         y=y,
                         ticks=yticks,
                         ticklabels=yticklabels,
                         minorticks=yminorticks,
                         label='-log10(q)',
                         invert=True,
                         title_offset=90)

    svg.add_text_bb('Depletion', x=x2-20, y=y+height/2,
                    size=core.FIGURE_FONT_SIZE, orientation='v', align='c')

    # svg.cluster_label_rows(row_labels,
    #                         clusters,
    #                         h=h,
    #                         showgroups=False,
    #                         showblocks=showblocks,
    #                         showlabels=showlabels,
    #                         invert_x=invert_x)

    return 0, height


def add_enrich_stack_plot(svg,
                          tables,
                          clusters,
                          cluster_groups,
                          x=0,
                          y=0,
                          height=300,
                          bar_width=8,
                          bar_gap=0,
                          block_gap=[5, 5],
                          bar_color=None,
                          bar_border='white',
                          ylim=[0, 100],
                          yticks=[0, 25, 50, 75, 100],
                          yticklabels=None,
                          yminorticks=None,
                          showyaxis=True,
                          colormap=core.ABC_COLORS,
                          stroke=core.STROKE_SIZE,
                          cluster_group_gap=50):
    # if smallfont:
    #    svg.set_font_size(core.FIGURE_FONT_SIZE)

    # enrich

    yaxis = Axis(lim=ylim, ticks=yticks, w=height)

    df_coo = tables[0].apply(lambda row: row / row.sum() * 100, axis=1)

    x2 = x + cluster_group_gap/2  # - yaxis.scale(yaxis.lim[1] - 0.5)

    # gray out section

    # draw bars

    ids = []

    for name in df_coo.index:
        if str(name) == 'nan':
            continue

        if name == 101:
            continue

        if isinstance(name, str):
            matcher = re.search(r'(\d+)', name)

            if matcher:
                ids.append(clusters.find(int(matcher.group(1))))
            else:
                ids.append(name)
        else:
            ids.append(clusters.find(name))

    ids = np.array(ids)

    x1 = x2

    y2 = y + height

    for row_block in cluster_groups:
        for label in row_block['items']:

            i = np.where(ids == label)[0]

            if i.size > 0:
                i = i[0]
            else:
                i = -1

            y3 = y2

            for j in range(df_coo.shape[1]):
                col = df_coo.columns[j]

                # col = col.split(' ')[0] #col.replace(' q', '') #col.split(' ')[0]

                color = colormap[col]

                if isinstance(color, tuple):
                    color = core.rgbtohex(color)

                v = df_coo.iloc[i, j]

                h = yaxis.scale(v)

                y1 = y3 - h

                svg.add_rect(x2 + bar_gap, y1, bar_width-2 *
                             bar_gap, h, fill=color, stroke=stroke)

                if bar_color is not None:
                    svg.add_rect(x2 + bar_gap, y1, bar_width-2 *
                                 bar_gap, h, color=bar_color, stroke=stroke)

                y3 -= h

                # if frame:
                #     w2 = xaxis.scale(v)
                #     #svg.add_frame(x, y3, w=w2, h=bar_width)

                #     svg.add_line(x1=x, y1=y3, x2=x+w2+stroke/2, y2=y3, stroke=stroke)
                #     svg.add_line(x1=x, y1=y3+bar_width, x2=x+w2+stroke/2, y2=y3+bar_width, stroke=stroke)
                #     svg.add_line(x1=x+w2, y1=y3, x2=x+w2, y2=y3+bar_width, stroke=stroke)

            if bar_border is not None:
                svg.add_rect(x2 + bar_gap, y1, bar_width-2*bar_gap,
                             height, color=bar_border, stroke=stroke)

            x2 += bar_width

            # break
        svg.add_line(x1=x1, y1=y+height, x2=x2, y2=y +
                     height, stroke=core.AXIS_STROKE)
        x2 += cluster_group_gap
        x1 = x2

    # dashed line
    #svg.add_rect(x, y2, x2-x, h, fill=sigqcolor)
    #svg.add_line(x1=x, y1=y2, x2=x2, y2=y2, dashed=True)

    #svg.add_line(x1=x, y1=y, x2=x2, y2=y, stroke=core.AXIS_STROKE)

    if showyaxis:
        svg.add_y_axis(axis=yaxis,
                       x=x,
                       y=y2,
                       ticks=yticks,
                       ticklabels=yticklabels,
                       minorticks=yminorticks,
                       label='% cells',
                       title_offset=90)

    return 0, height
