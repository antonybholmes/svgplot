#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: antony
"""
import collections
import numpy as np
import libplot
import matplotlib
import pandas as pd
import yaml
from . import core
from . import matrix
from .svgfigure import SVGFigure
from . import util


def add_single_split_heatmap(svg: SVGFigure,
							 expfile,
							 clusters,
							 rf,
							 cf,
							 x=0,
							 y=0,
							 cell=matrix.DEFAULT_CELL,
							 lim=matrix.DEFAULT_LIMITS,
							 splits=None,
							 block_gap=140,
							 indexmatch='Gene',
							 colmatch='fold change',  # 'tpm',
							 norm='none',  # 'z-score',
							 cmap=libplot.BWR2_CMAP,
							 gridcolor='black',  # core.GRID_COLOR,
							 padding=10,
							 showgrid=True,
							 showframe=True,
							 labelargs=None):
	"""
	A heatmap split into row and column blocks

	Parameter
	---------
	rf : str
			Rows to plot yaml file.
	cf : str
			Cols to plot yaml file.
	gf: str, optional
			YAML gene set file

	"""

	if splits is None:
		splits = set()

	splits.add(0)

	if labelargs is None:
		labelargs = {}

	if 'mode' not in labelargs:
		labelargs['mode'] = 'bars,clusters,short'
	if 'orientation' not in labelargs:
		labelargs['orientation'] = 'h'
	if 'bold' not in labelargs:
		labelargs['bold'] = False
	if 'grouporientation' not in labelargs:
		labelargs['grouporientation'] = 'v'
	if 'showlabels' not in labelargs:
		labelargs['showlabels'] = True
	if 'showsinglegroups' not in labelargs:
		labelargs['showsinglegroups'] = False
	if 'split' not in labelargs:
		labelargs['split'] = False
	if 'remap' not in labelargs:
		labelargs['remap'] = {}
	if 'rowfontsize' not in labelargs:
		labelargs['rowfontsize'] = core.FIGURE_FONT_SIZE

	row_sets = yaml.load(open(rf), Loader=yaml.SafeLoader)
	col_sets = yaml.load(open(cf), Loader=yaml.SafeLoader)

	# Extract the expression columns of interest
	df1 = pd.read_csv(expfile, sep='\t', header=0)
	df_exp1 = df1.iloc[:, np.where(df1.columns.str.contains(colmatch))[0]]
	df_exp1 = df_exp1.set_index(df1[indexmatch])
	df_exp1.to_csv('data.txt', sep='\t', header=True, index=True)

	if norm == 'z-score':
		df_z = util.zscore(df_exp1)
		df_z.to_csv('z.txt', sep='\t', header=True, index=True)
		df_fc_clipped = df_z.copy()
	else:
		df_fc_clipped = df_exp1.copy()

	df_fc_clipped[df_fc_clipped > lim[1]] = lim[1]
	df_fc_clipped[df_fc_clipped < lim[0]] = lim[0]

	df1 = df_fc_clipped  # df_fc_clipped.iloc[:, 0:df_exp1.shape[1]]

	df1.columns = [x.replace('Cluster ', '').replace(' log2 fold change', '').replace(
		' avg log2(tpm + 1)', '').replace('Avg log2(tpm + 1) in ', '') for x in df1.columns]

	mapper = matplotlib.cm.ScalarMappable(norm=matplotlib.colors.Normalize(vmin=lim[0], vmax=lim[1]),
										  cmap=cmap)

	hx = x

	block_width = block_gap

	for col_set in col_sets:
		block_width += len(col_set) * cell[0] + padding

	for split in splits:
		add_single_cell_col_labels(svg,
								   clusters,
								   col_sets,
								   pos=(hx, y),
								   cell=cell,
								   modes=labelargs['mode'],
								   orientation=labelargs['orientation'],
								   grouporientation=labelargs['grouporientation'],
								   showsinglegroups=labelargs['showsinglegroups'],
								   split=labelargs['split'],
								   remap=labelargs['remap'])

		hx += block_width

	#
	# heatmap
	#

	hx = x

	for col_set in col_sets:
		hy = y

		w = len(col_set) * cell[0]

		labels = []

		for i in range(0, len(row_sets)):
			row_set = row_sets[i]

			if isinstance(row_set, dict):
				name = row_set['name']
				genes = row_set['genes']
			else:
				name = None
				genes = row_set

			if i > 0 and i in splits:
				hy = y
				hx += block_width

			h = len(genes) * cell[1]
			hx2 = hx

			for col in col_set:
				hy2 = hy

				for gene in genes:
					#print(gene, col, df1.columns)
					ri = np.where(df1.index == gene)[0][0]
					ci = np.where((df1.columns == col) | (
						df1.columns == 'C{}'.format(col)))[0][0]
					v = df1.iloc[ri, ci]

					color = core.rgbatohex(mapper.to_rgba(v))
					svg.add_rect(hx2, hy2, cell[0], cell[1], fill=color)

					hy2 += cell[1]

				hx2 += cell[0]

			if showgrid:
				matrix.add_grid(svg,
								pos=(hx, hy),
								size=(w, h),
								shape=(len(genes), len(col_set)),
								color=gridcolor)

			if showframe:
				svg.add_frame(x=hx, y=hy, w=w, h=h)

			hy += h + padding

		hx += w + padding

	w = hx - padding
	h = hy - padding

	#
	# Row labels on right
	#

	hy = y
	hx = x

	# width of plot
	for col_set in col_sets:
		hx += len(col_set) * cell[0] + padding

	for i in range(0, len(row_sets)):
		row_set = row_sets[i]

		if isinstance(row_set, dict):
			name = row_set['name']
			genes = row_set['genes']
		else:
			name = None
			genes = row_set

		if i > 0 and i in splits:
			hy = y
			hx += block_width

		h = len(genes) * cell[1]

		labels = []

		for gene in genes:
			ri = np.where(df1.index == gene)[0][0]
			labels.append(df1.index[ri])

		hy2 = hy + cell[1] / 2

		for label in labels:
			svg.add_text_bb(label, x=hx, y=hy2)
			hy2 += cell[1]

		hy += h + padding

	#
	# block labels vertical down side
	#

	hy = y
	hx = x - 2 * padding

	for i in range(0, len(row_sets)):
		row_set = row_sets[i]

		if i > 0 and i in splits:
			hy = y
			hx += block_width

		if isinstance(row_set, dict):
			name = row_set['name']
			genes = row_set['genes']
		else:
			name = None
			genes = row_set

		if name is not None:
			h = len(genes) * cell[1]
			svg.add_text_bb(name, x=hx, y=hy + h, w=h,
							align='c', orientation='v')

		hy += h + padding


	return (w, h)


def add_single_cell_col_labels(svg: SVGFigure,
							   clusters,
							   col_sets,
							   pos: tuple = (0, 0),
							   cell=matrix.DEFAULT_CELL,
							   orientation:str ='h',
							   grouporientation:str='auto',
							   modes:str='short,bars',
							   padding:int=10,
							   linespacing:int=10,
							   ignore={},
							   split:bool=False,
							   frame:bool=False,
							   showunclass:bool=True,
							   showsinglegroups:bool=False,
							   remap={}):
	"""
	Label a heat map

	Parameters
	----------
	split: bool, optional
			True if labels should be split on space to form newlines
	"""
	
	x, y = pos

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
			gy -= padding/2
			gx = x  + cell[0] / 2

			# keep track of longest string to work out how much
			# vertical space to allocate
			sw = 0

			weight = 'normal'  # 'bold' if bold else 'normal'

			for g in group_map['clusters']:
				if g not in ignore:
					color = color_map[g]

					if orientation == 'v':
						svg.add_text_bb(g,
										x=gx,
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
					gx2 = gx # - svg.get_font_h() * 0.5
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

					gx2 = gx + gw/2 - (svg.get_font_h() +
					 			linespacing) / 2 * (len(words) - 1)
					#gx2 = gx
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