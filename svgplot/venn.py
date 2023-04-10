from typing import Optional

import numpy as np
from pandas import DataFrame

from .svgfigure import SVGFigure


def add_venn(svg: SVGFigure,
             data: DataFrame,
             x: Optional[str] = None,
             hue: Optional[str] = None,
             hue_order: Optional[list[str]] = None,
             palette: dict[str, str] = {},
             pos: tuple[float, float] = (0, 0),
             fill_opacity: float = 0.5,
             w: int = 250):
    """_summary_

    Args:
            svg (SVGFigure): _description_
            data (DataFrame): _description_
            pos (tuple[float, float], optional): _description_. Defaults to (0, 0).
            stroke (int, optional): _description_. Defaults to 4.
            title (Optional[str], optional): _description_. Defaults to ''.
            axes (tuple[Axis, Axis], optional): _description_. Defaults to None.
            xaxis_kws (Union[bool, str, Mapping[str, Union[int, float, str, bool]]], optional): _description_. Defaults to {}.
            yaxis_kws (Union[bool, str, Mapping[str, Union[int, float, str, bool]]], optional): _description_. Defaults to {}.
            color (str, optional): _description_. Defaults to 'black'.
            fill (str, optional): _description_. Defaults to 'none'.
            fill_opacity (float, optional): _description_. Defaults to 0.2.
            smooth (bool, optional): _description_. Defaults to False.

    Returns:
            _type_: _description_
    """

    svg.inc(x=w/2,y=w/2)

    xp, yp = pos

    if x is None:
        x = ''

    if hue is None:
        hue = ''

    if hue_order is None:
        if hue != '':
            hue_order = list(sorted(data[hue].unique()))
        else:
            hue_order = ['']  # sorted(data[x].unique())

    hue_order = np.array(hue_order)

    s1 = set(data[data[hue] == hue_order[0]].iloc[:, 0].values)
    s2 = set(data[data[hue] == hue_order[1]].iloc[:, 0].values)
    common = s1.intersection(s2)

    plot_data = {'010': len(common), '100': len(s1.difference(common)), '001': len(s2.difference(common))}

    print(plot_data)
    x2 = w * 0.6

    svg.add_circle(w=w, fill=palette[hue_order[0]], fill_opacity=fill_opacity)
    svg.add_circle(
        x=x2, w=w, fill=palette[hue_order[1]], fill_opacity=fill_opacity)

    svg.add_text_bb(f'{plot_data["100"]:,}', x=-w/5,
                    y=0, align='c', color='white')

    svg.add_text_bb(hue_order[0], x=0, y=-(w/2 + 30), align='c')

    svg.add_text_bb(f'{plot_data["001"]:,}', x=x2+w/5,
                    y=0, align='c', color='white')

    svg.add_text_bb(hue_order[1], x=x2, y=-(w/2 + 30), align='c')

    svg.add_text_bb(f'{plot_data["010"]:,}', x=x2/2,
                    y=0, align='c', color='white')
    
    svg.undo_t()

    return (w+x2, w)
