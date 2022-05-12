from typing import Optional
import numpy as np
from .svgfigure import SVGFigure
from .axis import Axis


def add_boxplot(svg: SVGFigure,
               data_points: np.array,
               axes: tuple[Axis, Axis],
               width:int = 18,
               whisker_width: Optional[int] = None,
               color: str = 'blue',
               fill: str = 'white',
               opacity: float = 1,
               stroke = 3,
               pos: tuple[int, int] = (0, 0),
               median_style: str = 'circle',
               dot_size: int = 12,
               rounded:bool = True):
    
    if whisker_width is None:
        whisker_width = width

    x, y = pos

    _, yaxis = axes

    q1, median, q3 = np.quantile(data_points, [0.25, 0.5, 0.75])

    iqr = q3 - q1
    iqr_15 = 1.5 * iqr
    q1_iqr = max(q1 - iqr_15, data_points.min())
    q3_iqr = min(q3 + iqr_15, data_points.max())

    #svg.add_rect(x=x-iqr_15_line_width/2, y=y+yaxis.w-yaxis.scale(q3_iqr), w=iqr_15_line_width, h=yaxis.scale(q3_iqr) - yaxis.scale(q1_iqr), fill='red', rounding=iqr_15_line_width)
    #svg.add_rect(x=x-iqr_line_width/2, y=y+yaxis.w-yaxis.scale(q3), w=iqr_line_width, h=yaxis.scale(q3) - yaxis.scale(q1), fill='red', rounding=iqr_line_width)

    #svg.add_rect(x=x-iqr_15_line_width/2, y=y+yaxis.w-yaxis.scale(q3_iqr), w=iqr_15_line_width, h=yaxis.scale(q3_iqr) - yaxis.scale(q1_iqr), color='black', fill='white', stroke=2)
    
    svg.add_line(x1=x, y1=y + yaxis.w-yaxis.scale(q3_iqr), y2=y+yaxis.w-yaxis.scale(q1_iqr), color=color, stroke=stroke)
    svg.add_line(x1=x-whisker_width/2, x2=x+whisker_width/2, y1=y+yaxis.w-yaxis.scale(q3_iqr), color=color, stroke=stroke)
    svg.add_line(x1=x-whisker_width/2, x2=x+whisker_width/2, y1=y+yaxis.w-yaxis.scale(q1_iqr), color=color, stroke=stroke)

    #svg.add_rect(x=x-iqr_line_width/2, y=y+yaxis.w-yaxis.scale(q3), w=iqr_line_width, h=yaxis.scale(q3)-yaxis.scale(median), fill='white', color=color, stroke=stroke, rounding=iqr_line_width/2)
    #svg.add_rect(x=x-iqr_line_width/2, y=y+yaxis.w-yaxis.scale(median), w=iqr_line_width, h=yaxis.scale(median)-yaxis.scale(q1), fill='white', color=color, stroke=stroke, rounding=iqr_line_width/2)

    svg.add_rect(x=x-width/2, y=y+yaxis.w-yaxis.scale(q3), w=width, h=yaxis.scale(
        q3) - yaxis.scale(q1), stroke=stroke, fill=fill, fill_opacity=opacity, color=color, rounding=min(10, width/2) if rounded else 0)
    
    y1 = y+yaxis.w-yaxis.scale(median)

    match median_style:
        case 'circle':
            svg.add_circle(x=x, y=y1, w=dot_size, fill=color)
        case _:
            svg.add_line(x1=x-width/2, x2=x+width/2, y1=y1, color=color)