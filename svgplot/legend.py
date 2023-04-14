from typing import Mapping, Optional, Union
from .svgfigure import SVGFigure


def add_legend(svg: SVGFigure,
               hue_order: list[str],
               palette: Optional[Union[str, list[str],
                                       Mapping[str, str]]] = None,
               pos: tuple[int, int] = (0, 0),
               fill_opacity: Optional[Union[float,
                                            str, Mapping[str, float]]] = 1,
               style='bullet'):
    """Adds a legend to the plot

    Args:
        svg (SVGFigure): _description_
        hue_order (list[str]): _description_
        palette (Optional[Union[str, list[str], Mapping[str, str]]], optional): _description_. Defaults to None.
        pos (tuple[int, int], optional): _description_. Defaults to (0, 0).
        fill_opacity (Optional[Union[float, str, Mapping[str, float]]], optional): _description_. Defaults to 1.
        style (str, optional): Legend style, either 'line' or 'bullet'. Defaults to 'bullet'.
    """
    colors = None

    if palette is not None:
        if isinstance(palette, str):
            colors = {ho: palette for ho in hue_order}
        elif isinstance(palette, list):
            colors = {ho: palette[i % len(palette)]
                      for i, ho in enumerate(hue_order)}
        elif isinstance(palette, dict):
            colors = palette
        else:
            pass

    if colors is None:
        colors = {ho: 'black' for ho in hue_order}

    if isinstance(fill_opacity, str):
        opacity = {ho: fill_opacity for ho in hue_order}
    elif isinstance(fill_opacity, list):
        opacity = {ho: palette[i % len(fill_opacity)]
                   for i, ho in enumerate(hue_order)}
    elif isinstance(fill_opacity, dict):
        opacity = fill_opacity
    else:
        opacity = {ho: 1 for ho in hue_order}

    x, y = pos

    if style == 'line':
        for ho in hue_order:
            svg.add_line(x2=50, y1=y, color=colors[ho], stroke=4)
            svg.add_text_bb(ho, x=70, y=y)
            y += 40
    else:
        for ho in hue_order:
            svg.add_bullet(
                ho, x=x, y=y, color=colors[ho], fill_opacity=opacity[ho])
            y += 40
