# svgplot

A library for creating plots directly onto SVG. This is to allow for consistent use of fonts and sizes on
a multi-panel svg plot without having to fight with matplotlib's less than stellar sizing options. In
this library the size of the plot is usually governed by the axis size or block size in a heat map and
everything is relative to this. This is to allow plots to have a precise size rather than messing around
with matplotlibs sizing and borders to get something that is about the right size.

First an svg canvas is created using a default 12x12 grid to allow for easy placement of sub panels. In
reality you can place anything anywhere you want, the grid is provided as a guide should you want to
use it. The subgrid is formed by converting the size in inches to mm and multiplying by 10.

Plots are added via simple methods such as add_heatmap which should be familiar to anyone who has
used Seaborn. Typically methods take pandas dataframes as input.

Unlike matplotlib you do not have an object representation of the graph that can be adjusted later, 
all parameters must be stated upfront. On the other hand all methods are more transparent rather
than being hidden in poorly documented object structures as with matplotlib.

# Offset

Call svg.set_cell(x, y) to move the renderer to a point on the canvas based on the 12x12 grid. All
drawing will then become relative to this origin.

Call svg.t(x, y) to tranlate from the origin defined by set_cell to get more granular control over
the position.
