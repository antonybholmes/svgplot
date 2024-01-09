import collections

from . import core
from .svgfigure import SVGFigure

DEFAULT_CELL = [30, 26]
DEFAULT_LIMITS = [-2, 2]


def heatmap_label_cols(svg: SVGFigure,
                       clusters,
                       col_sets: list[str],
                       x: int = 0,
                       y: int = 0,
                       cell=DEFAULT_CELL,
                       orientation: str = 'h',
                       grouporientation: str = 'auto',
                       modes: str = 'clusters,short,bars',
                       colorlabels: bool = True,
                       padding: int = 10,
                       linespacing: int = 10,
                       ignore={},
                       split: bool = False,
                       frame: bool = False,
                       showunclass: bool = True,
                       showsinglegroups: bool = False,
                       remap={},
                       weight: str = 'normal'):
    """
    Label a heat map

    Parameters
    ----------
    split: bool, optional
        True if labels should be split on space to form newlines
    """

    if isinstance(modes, str):
        modes = modes.split(',')

    modes = set(modes)

    # Since we can rename groups, we store the colors separately to
    # the main cluster objects
    group_map = collections.defaultdict(
        lambda: collections.defaultdict(set))
    color_map = {}
    block_color_map = {}

    hx = x
    hy = y

    h = core.LABEL_COLOR_BLOCK_SIZE  # cell[1] / 2

    for col_set in col_sets:
        w = len(col_set) * cell[0]
        hx2 = hx

        for i in range(0, len(col_set)):
            col = col_set[i]

            altId = clusters.find(
                col) if clusters is not None else str(col)

            color = clusters.get_color(
                altId) if clusters is not None else 'black'

            for mode in modes:
                if mode == 'short':
                    group = clusters.get_short_group(
                        altId) if clusters is not None else str(col)
                elif mode == 'group':
                    group = clusters.get_group(
                        altId) if clusters is not None else str(col)
                else:
                    group = altId

                color = clusters.get_color(
                    group) if clusters is not None else 'black'
                block_color = clusters.get_block_color(
                    group) if clusters is not None else 'black'

                if group in remap:
                    group = remap[group]

                group_map[mode][group].add(i)
                color_map[group] = color
                block_color_map[group] = block_color

            hx2 += cell[0]

        gy = hy - padding

        #
        # plot color bar
        #

        if 'bars' in group_map:
            gy -= h
            gx = x  # + cell[0] / 2

            # keep track of longest string to work out how much
            # vertical space to allocate
            sw = 0

            c = 0

            for g in group_map['bars']:
                if g not in ignore:
                    color = color_map[g]

                    svg.add_rect(gx, gy, cell[0], h, fill=color)

                    if c > 0:
                        svg.add_line(x1=gx, y1=gy-2, x2=gx,
                                     y2=gy+h+2, color='white')

                    if frame:
                        svg.add_frame(gx, gy, cell[0], h)

                gx += cell[0]

                c += 1

            gy -= padding

        #
        # plot cluster id first
        #

        if 'clusters' in group_map:
            gy -= padding
            gx = x  # + cell[0] / 2

            # keep track of longest string to work out how much
            # vertical space to allocate
            sw = 0

            weight = 'normal'  # 'bold' if bold else 'normal'

            for g in group_map['clusters']:
                if g not in ignore:
                    color = color_map[g] if colorlabels else 'black'

                    if orientation == 'v':
                        svg.add_text_bb(g,
                                        x=gx + cell[0] / 2 + 3,
                                        y=gy,
                                        w=cell[0],
                                        color=color,
                                        orientation='v',
                                        weight=weight)

                        sw = max(sw, svg.get_string_width(g))
                    else:
                        svg.add_text_bb(g,
                                        gx,
                                        gy,
                                        w=cell[0],
                                        color=color,
                                        orientation='h',
                                        weight=weight)

                        sw = svg.get_font_h()

                gx += cell[0]

            gy -= sw

        #
        # Plot group label second
        #

        if 'short' in group_map:
            gy2 = gy  # - core.BRACKET_SIZE
            gy = gy2 - 2 * padding

            for g in group_map['short']:
                if g in ignore:
                    continue

                if not showsinglegroups and len(group_map['short'][g]) < 2:
                    continue

                s = min(group_map['short'][g])
                e = max(group_map['short'][g])

                gx = x + s * cell[0]
                gw = (e - s + 1) * cell[0]

                color = block_color_map[g]

                if grouporientation == 'a':
                    # plot at 45 deg angle
                    gx2 = gx - svg.get_font_h() * 0.5
                    svg.add_text_bb(g,
                                    x=gx2,
                                    y=gy,
                                    w=gw,
                                    color=color,
                                    orientation='a',
                                    weight=weight)
                elif ((grouporientation == 'auto') and (len(group_map['short'][g]) < 3 and len(g) > 1)) or grouporientation == 'v':
                    if not showunclass and 'unclass' in g.lower():
                        continue

                    if isinstance(split, bool) and split:
                        words = g.split(' ')
                        words = [' '.join(words[0:-1]), words[-1]]
                    elif isinstance(split, set) and g in split:
                        words = g.split(' ')
                        words = [' '.join(words[0:-1]), words[-1]]
                    else:
                        words = [g]

                    gx2 = gx - (svg.get_font_h() +
                                linespacing) / 2 * (len(words) - 1)

                    for word in words:
                        svg.add_text_bb(word,
                                        x=gx2,
                                        y=gy,
                                        w=gw,
                                        color=color,
                                        orientation='v',
                                        weight=weight)
                        gx2 += svg.get_font_h() + linespacing

                else:
                    # horizontal labels
                    if showunclass or 'unclass' not in g.lower():
                        svg.add_text_bb(g,
                                        gx,
                                        gy,
                                        w=gw,
                                        align='c',
                                        color=color,
                                        weight=weight)

                if len(group_map['short'][g]) == 1:
                    pass
                else:
                    svg.add_line(x1=gx + padding,
                                 y1=gy2,
                                 x2=gx + gw - padding,
                                 y2=gy2,
                                 color=color)

        hx += w + padding
