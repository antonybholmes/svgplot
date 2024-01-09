
import numpy as np
import pandas as pd

from . import heatmap
from .svgfigure import SVGFigure


def pathway_heatmap(svg: SVGFigure,
                    file,
                    clusters,
                    x=0,
                    y=0,
                    gene_sets=[],
                    cell=heatmap.DEFAULT_CELL,
                    lim=heatmap.DEFAULT_LIMITS,
                    cluster_sets=None,
                    colorlabels=True,
                    gridcolor='black',  # core.GRID_COLOR,
                    # 'red', #'#aaaaaa',
                    pathwaycolor=['darkgray', 'dimgray'],
                    padding=10,
                    showgrid=True,
                    showframe=True,
                    labelargs=None,
                    showunclass=True,
                    labelrows=True,
                    ignore={},
                    labelcase='mixed'):
    """ 
    A heatmap split into row and column blocks

    Parameter
    ---------
    gf: str, optional
        YAML gene set file

    """

    if labelargs is None:
        labelargs = {}

    if 'mode' not in labelargs:
        labelargs['mode'] = 'cluster,bars,short'
    if 'orientation' not in labelargs:
        labelargs['orientation'] = 'h'
    if 'showlabels' not in labelargs:
        labelargs['showlabels'] = True
    if 'showsinglegroups' not in labelargs:
        labelargs['showsinglegroups'] = False
    if 'grouporientation' not in labelargs:
        labelargs['grouporientation'] = 'h'
    if 'split' not in labelargs:
        labelargs['split'] = False

    if isinstance(file, str):
        file = [file]

    files = np.array(file)

    if cluster_sets is None:
        cluster_sets = []

    for f in files:
        df = pd.read_csv(f, sep='\t', header=0)

        for c in df['Gene Set'].values:
            if c not in gene_sets and c.lower() not in ignore:
                gene_sets.append(c)

        # for c in df['Cluster'].values:
        #     if c not in cluster_sets:
        #         cluster_sets.append(c)

    cluster_sets = np.array(cluster_sets)

    gene_sets = np.array(gene_sets)

    d = np.zeros((gene_sets.size, cluster_sets.size), dtype=int)

    c = 1

    for f in files:
        df = pd.read_csv(f, sep='\t', header=0)

        for i in range(0, gene_sets.size):
            for j in range(0, cluster_sets.size):
                # convert display to to cluster id
                print(j, cluster_sets[j])
                cid = clusters.display_id_to_id(cluster_sets[j])

                print(cid, cluster_sets[j], 'oats')

                d[i, j] += c if np.where((df['Gene Set'] == gene_sets[i]) & (
                    df['Cluster'] == 'C{}'.format(cid)))[0].size > 0 else 0

        c += 1

    print(d)

    heatmap.heatmap_label_cols(svg,
                               clusters,
                               np.array([cluster_sets]),
                               x=x,
                               y=y,
                               cell=cell,
                               colorlabels=colorlabels,
                               modes=labelargs['mode'],
                               split=labelargs['split'],
                               orientation='v',
                               grouporientation=labelargs['grouporientation'],
                               showunclass=showunclass,
                               showsinglegroups=labelargs['showsinglegroups'])

    #
    # heatmap
    #

    hy = y

    for i in range(0, gene_sets.size):
        hx = x

        for j in range(0, cluster_sets.size):
            v = d[i, j]

            if v == 1:
                # core.rgbatohex(mapper.to_rgba(v))
                color = pathwaycolor[0]
                svg.add_rect(hx, hy, cell[0], cell[1], fill=color)
            elif v == 2:
                # core.rgbatohex(mapper.to_rgba(v))
                color = pathwaycolor[1]
                svg.add_rect(hx, hy, cell[0], cell[1], fill=color)
            elif v == 3:
                color = pathwaycolor[0]
                svg.add_rect(hx, hy, cell[0]/2, cell[1], fill=color)
                color = pathwaycolor[1]
                svg.add_rect(hx+cell[0]/2, hy,
                             cell[0]/2, cell[1], fill=color)
            else:
                color = 'white'
                svg.add_rect(hx, hy, cell[0], cell[1], fill=color)

            hx += cell[0]

        hy += cell[1]

    if showgrid:
        svg.add_grid(x=x,
                     y=y,
                     w=hx,
                     h=hy,
                     rows=d.shape[0],
                     cols=d.shape[1],
                     color=gridcolor)

    if showframe:
        svg.add_frame(x=x, y=y, w=hx, h=hy)

    w = hx
    h = hy

    #
    # Row labels
    #

    if labelrows:
        # svg.set_font_size(core.FIGURE_FONT_SIZE)

        hx = w + padding
        # add small offset to make it look better
        hy = y + cell[1] / 2 + 3

        for gene_set in gene_sets:
            gene_set = gene_set.replace('HALLMARK', 'HM')
            gene_set = gene_set.replace('KEGG', 'KG')
            gene_set = gene_set.replace('_PATHWAY', '')
            #gene_set = gene_set.replace('RESPONSE', 'RESP')
            gene_set = gene_set.replace('SIGNALING', 'SIGNAL')
            #gene_set = gene_set.replace('PHOSPHORYLATION', 'PHOS')
            #gene_set = gene_set.replace('REPAIR', 'REP')
            #gene_set = gene_set.replace('REPLICATION', 'REP')
            gene_set = gene_set.replace('NUCLEOTIDE', 'NT')
            #gene_set = gene_set.replace('APOPTOSIS', 'APOPT')

            if labelcase == 'lower':
                gene_set = gene_set.lower()

            if labelcase == 'upper':
                gene_set = gene_set.upper()

            svg.add_text_bb(gene_set, x=hx, y=hy)
            hy += cell[1]

        # svg.set_font_size(core.DEFAULT_FONT_SIZE)

    return (w, h)
