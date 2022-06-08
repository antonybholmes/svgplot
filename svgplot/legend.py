from typing import Mapping, Optional, Union
from .svgfigure import SVGFigure


def add_legend(svg: SVGFigure,
               hue_order: list[str],
               palette: Union[str, Mapping[str, str]],
               pos: tuple[int, int] = (0, 0),
               fill_opacity: Optional[Union[float, str, Mapping[str, float]]] = 1):
    
    if isinstance(palette, str):
        colors = {ho:palette for ho in hue_order}
    elif isinstance(palette, list):
        colors = {ho:palette[i % len(palette)] for i, ho in enumerate(hue_order)}
    elif isinstance(palette, dict):
        colors = palette
    else:
        colors = {ho:'black' for ho in hue_order}

    if isinstance(fill_opacity, str):
        opacity = {ho:fill_opacity for ho in hue_order}
    elif isinstance(fill_opacity, list):
        opacity = {ho:palette[i % len(fill_opacity)] for i, ho in enumerate(hue_order)}
    elif isinstance(fill_opacity, dict):
        opacity = fill_opacity
    else:
        opacity = {ho:1 for ho in hue_order}

    x, y = pos
    for ho in hue_order:
        svg.add_bullet(ho, x=x, y=y, color=colors[ho], fill_opacity=opacity[ho])
        y += 40