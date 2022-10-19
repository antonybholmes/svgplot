import numpy as np
from .svgfigure import SVGFigure
from .axis import Axis

ARROW_GAP = 20
ARROW_LEAN = 6
GENE_LINE_GAP = 40
EXON_HEIGHT = 30
GENE_TEXT_OFFSET = 20
BIG_ARROW_SIZE = 30
LEGEND_ROW_H = 40
LEGEND_DOT_SIZE = 10
LEGEND_DOT_Y_OFFSET = (LEGEND_ROW_H - LEGEND_DOT_SIZE) / 2


def plot_gene_diagrams(svg: SVGFigure,
                       transcripts: list[dict],
                       xaxis: Axis,
                       pos: tuple[float, float] = (0, 0),
                       align: str = 'right') -> None:

    x, y = pos

    for transcripti, transcript in enumerate(transcripts):

        # if gset[0] not in gene['ids']['gene_name']:
        #    continue

        # if genec == 3:
        #    break

        #chr, loc = gene['loc'].split(':')
        #start, end = [int(x) for x in loc.split('-')]
        #strand = gene['strand'] == '+'

        chr = transcript['chr']
        start = transcript['s']
        end = transcript['e']
        strand = transcript['str'] == '+'

        svg.add_line(x1=x+xaxis.scale_clip(start),
                     x2=x+xaxis.scale_clip(end))

        x1 = x + xaxis.scale_clip(start) + ARROW_GAP
        x2 = x1 + (-ARROW_LEAN * 1.5 if strand else ARROW_LEAN * 1.5)
        xmax = x+xaxis.scale_clip(end)

        while x2 < xmax:
            #print('arrow', x1, -ARROW_LEAN, x2, xmax)
            svg.add_line(x1=x1, y2=-ARROW_LEAN, x2=x2)
            svg.add_line(x1=x1, y2=ARROW_LEAN, x2=x2)

            x1 += ARROW_GAP
            x2 += ARROW_GAP

            # break

        max_x = 0

        for exon in transcript['exons']:
            #chr, loc = exon['loc'].split(':')
            #start, end = [int(x) for x in loc.split('-')]

            chr = exon['chr']
            exon_start = exon['s']
            exon_end = exon['e']

            x1 = x + xaxis.scale_clip(exon_start)
            x2 = x + xaxis.scale_clip(exon_end)
            w = x2 - x1
            #print('exon', start, end, x1, x2)

            if w > 0:
                svg.add_rect(x=x1, y=-EXON_HEIGHT/2, w=x2 -
                             x1, h=EXON_HEIGHT, fill='black')

        # if transcripti == 0:
        # gene #transcript['ids']['transcript_name'] #re.sub(r'_.+', '', gene['ids']['gene_name'].replace('Bernstein_', '').replace('CB4_', '').replace('H3K27ac_', ''))
        label = transcript['ids']['gene_name']

        if align == 'left':
            # accomodate annoying labels that run into next figure
            svg.add_text_bb(label, x=x-svg.get_string_width(label))
        else:
            #svg.add_text_bb(label, x=xoffset+xaxis.scale_clip(max_end) + 20)
            svg.add_text_bb(label, x=x+xaxis.scale_clip(exon_end) + 20)

        # big arrow
        x1 = x + xaxis.scale_clip(start if strand else end)
        svg.add_line(x1=x1, y1=0, x2=x1, y2=-BIG_ARROW_SIZE)

        s = BIG_ARROW_SIZE * 0.5
        s2 = s * 2

        if strand:
            svg.add_line(x1=x1, y1=-BIG_ARROW_SIZE, x2=x1 +
                         BIG_ARROW_SIZE/2, y2=-BIG_ARROW_SIZE)

            points = np.array([(x1 + BIG_ARROW_SIZE/2, -BIG_ARROW_SIZE - s),
                               (x1 + BIG_ARROW_SIZE/2, -BIG_ARROW_SIZE + s),
                               (x1 + BIG_ARROW_SIZE/2 + s2, -BIG_ARROW_SIZE)], dtype=float)

            svg.add(svg.trans(svg.base_polygon(points, fill='black')))
        else:
            svg.add_line(x1=x1-BIG_ARROW_SIZE/2, y1=-
                         BIG_ARROW_SIZE, x2=x1, y2=-BIG_ARROW_SIZE)

            points = np.array([(x1 - BIG_ARROW_SIZE/2, -BIG_ARROW_SIZE - s),
                               (x1 - BIG_ARROW_SIZE/2, -BIG_ARROW_SIZE + s),
                               (x1 - BIG_ARROW_SIZE/2 - s2, -BIG_ARROW_SIZE)], dtype=float)

            svg.add(svg.trans(svg.base_polygon(points, fill='black')))

        svg.inc(y=GENE_LINE_GAP)


def add_vert_cluster_legend(svg: SVGFigure,
                            clusters,
                            x=0,
                            y=0,
                            h=LEGEND_ROW_H,
                            padding=10,
                            min_group_size=2,
                            split_labels=True,
                            annotate_clusters=True,
                            annotate_groups=True,
                            show_group_labels=True,
                            shortgroupnames=False,
                            shape='c',
                            index=False,
                            mapping=None,
                            excludegroups={},
                            weight='normal'):
    groups = []
    used = set()

    bracket_offset = 30

    # bracket_offset=svgplot.LEGEND_BRACKET_OFFSET,

    if annotate_clusters:
        maxl = 0

        for i in range(0, clusters.size):
            id = clusters.get_id(i)
            maxl = max(maxl, svg.get_string_width(id))

        bracket_offset += maxl + 10

    # find unique groups
    for i in range(0, clusters.size):
        id = clusters.get_id(i)

        # id #.split(' ')[0] #re.sub(r' .+', '', altId)
        group = clusters.get_group(id)

        if group not in used:
            groups.append(group)
            used.add(group)

    pc = 1

    for group in groups:
        ids = clusters.get_ids(group)

        print('test', group, excludegroups)

        if annotate_groups and ids.size >= min_group_size and group not in excludegroups:
            color = clusters.get_block_color(group)

            # len(set(clusters['Display Id'].values[np.where(clusters['Display Id'].str.contains(group))[0]])) * h
            bh = (ids.size - 1) * h

#                svg.add_line(x + bracket_offset - svgplot.BRACKET_SIZE,
#                              y,
#                              x + bracket_offset,
#                              y,
#                              color=color)
#
            if bh > 0:
                svg.add_line(x + bracket_offset,
                             y - svg.get_font_h() / 2 + padding / 2,
                             x + bracket_offset,
                             y + bh + svg.get_font_h() / 2 - padding / 2,
                             color=color)

#                    svg.add_line(x + bracket_offset - svgplot.BRACKET_SIZE,
#                                  y + bh,
#                                  x + bracket_offset,
#                                  y + bh,
#                                  color=color)
            if shortgroupnames:
                words = clusters.get_short_group(clusters.find(group))
            else:
                words = group

            if split_labels:
                words = words.split(' ')
            else:
                words = [words]

            ty = y + (bh - len(words) * svg.get_font_h() -
                      padding * (len(words) - 1)) / 2 + svg.get_font_h()

            #ty -= svg.get_font_h() * (len(words) - 1) + padding * 0.5 * (len(words) - 1)

            if show_group_labels:
                for word in words:
                    svg.add_text(word,
                                 x + bracket_offset + 10,
                                 ty,
                                 h=h,
                                 color=color,
                                 weight=weight)

                    ty += svg.get_font_h() + padding

            # if len(idx) > 1:
            used = set()
            names = []

            for id in ids:
                if id not in used:
                    names.append(id)
                    used.add(id)

            for n in names:
                color = clusters.get_color(n)

                if index:
                    svg.add_text_bb(str(pc), x=x-20, y=y, align='r')

                if annotate_clusters:
                    cid = clusters.display_id_to_id(n)

                    if mapping is not None:
                        cids = mapping.get(cid, [])
                    else:
                        cids = []
                        #n = '{} ({})'.format(n, ', '.join(mapping[cid]))

                    y1 = y + max(0, len(cids) - 1) * h / 2

                    svg.add_bullet(n, x, y1, color=color, h=h, shape=shape)

                    bh = (max(1, len(cids))) * h

                    if len(cids) > 0:
                        y1 = y - h / 2
                        y2 = y1 + bh
                        svg.add_line(x + bracket_offset,
                                     y1 + padding / 2,
                                     x + bracket_offset,
                                     y2 - padding / 2,
                                     color=color)

                        y1 = y

                        for mcid in cids:
                            svg.add_text_bb(
                                mcid, x=x + bracket_offset + 20, y=y1, color=color)
                            y1 += h
                else:
                    svg.add_bullet('', x, y, color=color, h=h, shape=shape)
                    bh = h

                y += bh
                #svg.add_line(x1=x, y1=y, x2=x+200, y2=y)

            pc += 1
