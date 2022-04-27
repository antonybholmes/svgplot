import numpy as np
from .svgfigure import SVGFigure
from .axis import Axis

ARROW_GAP = 20
ARROW_LEAN = 6
GENE_LINE_GAP = 40
EXON_HEIGHT = 30
GENE_TEXT_OFFSET = 20
BIG_ARROW_SIZE = 30

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
            print('strand')
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