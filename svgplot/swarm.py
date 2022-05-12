from typing import Any, Optional
from .svgfigure import SVGFigure
import numpy as np
from .axis import Axis


def add_swarm(svg: SVGFigure,
               data_points: np.array,
               axes: tuple[Axis, Axis],
               dot_size: int = 8,
               color: str = 'blue',
               fill: Optional[str] = None,
               opacity: float = 0.3,
               pos: tuple[int, int] = (0, 0),
               style: str = '.'):
    """Add a swarm plot

    Args:
        svg (SVGFigure): _description_
        data_points (np.array): _description_
        axes (tuple[Axis, Axis]): _description_
        dot_size (int, optional): _description_. Defaults to 8.
        color (str, optional): _description_. Defaults to 'blue'.
        fill (Optional[str], optional): _description_. Defaults to None.
        opacity (float, optional): _description_. Defaults to 0.3.
        pos (tuple[int, int], optional): _description_. Defaults to (0, 0).
        style (str, optional): _description_. Defaults to '.'.
    """               
    if fill is None:
        fill = color

    x, y = pos

    xaxis, yaxis = axes

    dot_r = dot_size / 2

    dot_positions = [y + yaxis.w - yaxis.scale(p) for p in sorted(data_points)]

    groups = []

    x_lim = [x - xaxis.w, x + xaxis.w]

    for p in dot_positions:
        found = False

        p1 = p - dot_r
        p2 = p + dot_r

        for group in groups:
            if (p1 >= group['x1'] and p1 <= group['x2']) or (p2 >= group['x1'] and p2 <= group['x2']):
                group['dots'].append(p)
                # make group more inclusive
                #group['x1'] = min(group['x1'], p1)
                #group['x2'] = max(group['x2'], p2)
                found = True
                break

        if not found:
            groups.append({'x1': p1, 'x2': p2, 'dots': [p]})

    for group in groups:
        x2 = x - (len(group['dots']) - 1) * dot_size / 2
        l = (len(group['dots']) - 1) * dot_size
        # shift points

        # prevent dots from expanding beyond confines of plot
        
        
        #if x3 != x2:
        #print(x2, x3, x_lim, l)

        for i, p in enumerate(reversed(group['dots'])):
            x3 = max(x_lim[0], min(x_lim[1], x2))

            match style:
                case '+':
                    svg.add_line(x1=x3-dot_size/2, x2=x3+dot_size/2, y1=p, color=color)
                    svg.add_line(x1=x3, y1=p-dot_size/2, y2=p+dot_size/2, color=color)
                case '^':
                    h = np.sin(np.pi / 3) * dot_size
                    svg.add_polygon([[x3-dot_size/2, p+h/2], [x3, p-h/2], [x3+dot_size/2, p+h/2]], fill=fill, fill_opacity=opacity)
                case _:
                    svg.add_circle(x=x3, y=p, w=dot_size,
                                fill=fill, fill_opacity=opacity)

            if i % 2 == 0:
                x2 += l
            else:
                x2 -= l

            l -= dot_size