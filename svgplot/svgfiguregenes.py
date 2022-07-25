import math
from typing import Optional
import numpy as np
import re
import os
import collections
from . import axis
from . import svgplot
from .svgfigureheatmap import SVGFigureHeatmap


class SVGFigureGenes(SVGFigureHeatmap):
    def __init__(self,
                 file,
                 size: tuple[float, float] = (279, 216),
                 view: Optional[tuple[int, int]] = None, #(2790, 2160),
                 grid=(12, 12),
                 border=100):
        super().__init__(file,
                         size=size,
                         view=view,
                         grid=grid,
                         border=border)

    def add_vert_legend(self,
                        clusters,
                        x=0,
                        y=0,
                        h=svgplot.LEGEND_ROW_H,
                        padding=10,
                        min_group_size=2,
                        split_labels=True,
                        annotate_clusters=True,
                        annotate_groups=True,
                        show_group_labels=True,
                        shortgroupnames=False,
                        shape='c',
                        index=False,
                        mapping=None,
                        excludegroups={},
                        weight='normal'):
        groups = []
        used = set()
        
        bracket_offset = 30
        
        #bracket_offset=svgplot.LEGEND_BRACKET_OFFSET,
        
        if annotate_clusters:
            maxl = 0
            
            for i in range(0, clusters.size):
                id = clusters.get_id(i)
                maxl = max(maxl, self.get_string_width(id))
                
            
            bracket_offset += maxl + 10
            

        # find unique groups
        for i in range(0, clusters.size):
            id = clusters.get_id(i)

            # id #.split(' ')[0] #re.sub(r' .+', '', altId)
            group = clusters.get_group(id)

            if group not in used:
                groups.append(group)
                used.add(group)
        
        pc = 1
        
        for group in groups:
            ids = clusters.get_ids(group)
            
            print('test', group, excludegroups)

            if annotate_groups and ids.size >= min_group_size and group not in excludegroups:
                color = clusters.get_block_color(group)


                # len(set(clusters['Display Id'].values[np.where(clusters['Display Id'].str.contains(group))[0]])) * h
                bh = (ids.size - 1) * h

#                self.add_line(x + bracket_offset - svgplot.BRACKET_SIZE, 
#                              y,
#                              x + bracket_offset, 
#                              y, 
#                              color=color)
#                
                if bh > 0:
                    self.add_line(x + bracket_offset, 
                                  y - self.get_font_h() / 2 + padding / 2, 
                                  x + bracket_offset, 
                                  y + bh + self.get_font_h() / 2 - padding / 2, 
                                  color=color)
                    
#                    self.add_line(x + bracket_offset - svgplot.BRACKET_SIZE, 
#                                  y + bh, 
#                                  x + bracket_offset, 
#                                  y + bh, 
#                                  color=color)
                if shortgroupnames:
                   words = clusters.get_short_group(clusters.find(group))
                else:
                   words = group

                if split_labels:
                    words = words.split(' ')
                else:
                    words = [words]

                ty = y + (bh - len(words) * self.get_font_h() -
                          padding * (len(words) - 1)) / 2 + self.get_font_h()

                #ty -= self.get_font_h() * (len(words) - 1) + padding * 0.5 * (len(words) - 1)
                
                if show_group_labels:
                    for word in words:
                        self.add_text(word, 
                                  x + bracket_offset + 10,
                                  ty, 
                                  h=h, 
                                  color=color, 
                                  weight=weight)

                        ty += self.get_font_h() + padding

                # if len(idx) > 1:
                used = set()
                names = []
                
                for id in ids:
                    if id not in used:
                        names.append(id)
                        used.add(id)
            

                for n in names:
                    color = clusters.get_color(n)

                    print('g', n, color)
                    
                    if index:
                        self.add_text_bb(str(pc), x=x-20, y=y, align='r')
                        
                    
                    if annotate_clusters:
                        cid = clusters.display_id_to_id(n)
                        
                        if mapping is not None:
                            cids = mapping.get(cid, [])
                        else:
                            cids = []
                            #n = '{} ({})'.format(n, ', '.join(mapping[cid]))
                                
                        
                        
                        y1 = y + max(0, len(cids) - 1) * h / 2
                        
                        self.add_bullet(n, x, y1, color=color, h=h, shape=shape)
                        
                        bh = (max(1, len(cids))) * h
                        
                        if len(cids) > 0:
                            y1 = y - h / 2
                            y2 = y1 + bh
                            self.add_line(x + bracket_offset, 
                                          y1 + padding / 2, 
                                          x + bracket_offset, 
                                          y2 - padding / 2, 
                                          color=color)
                            
                            y1 = y
                            
                            for mcid in cids:
                                self.add_text_bb(mcid, x=x + bracket_offset + 20, y=y1, color=color)
                                y1 += h
                            
                    else:
                        self.add_bullet('', x, y, color=color, h=h, shape=shape)
                        bh = h
                    
                    y += bh
                    #self.add_line(x1=x, y1=y, x2=x+200, y2=y)
                
                pc += 1
                

    def add_hoz_exp(self,
                    name,
                    exp_plots=[('PCNA', '(S)'), ('MKI67', '(G2-M)'),
                               ('CDK1', '(Entering M)'), ('CDC20', '(M)')],
                    x=0,
                    y=0,
                    w=250,
                    padding=40,
                    cols=5,
                    colormap='bgy'):

        startx = x
        starty = y

        dir = svgplot.find_gene_exp_dir(name, colormap=colormap)

        max_h = 0
        hf = self.get_font_h()

        c = 0

        for exp_plot in exp_plots:
            gene = exp_plot[0]
            
            if len(exp_plot) > 1:
                sub_heading = exp_plot[1]
            else:
                sub_heading = ''

            file = svgplot.find_exp_file(gene, dir)
            self.add_image(file, x=x, y=y, w=w, title=gene,
                           subtitle=sub_heading)
            h = svgplot.scaled_image_h(file, w)
            max_h = max(max_h, h)

            #self.add_frame(x, start_y + h + padding + hf, w, hf)

            x += w + padding

            c += 1

            if c == cols:
                x = startx
                y += max_h + 3 * hf + 2 * padding
                c == 0
                
        return x

    def add_colorbar(self,
                     x=0,
                     y=0,
                     w=120,
                     name='bgy',
                     label1='Low',
                     label2='High',
                     dir=svgplot.COLORBAR_DIR,
                     orientation='h',
                     padding=10,
                     align='l'):
        sw1 = self.get_string_width(label1)
        sw2 = self.get_string_width(label2)
        

        h = self.get_font_h()

        file = '{}/{}_colorbar.png'.format(dir, name)

        w, h, image = self.base_image(file, w=w)
        hf = svgplot.scaled_image_h(file, w)
        
        cw = sw1 + padding + w + padding + sw2
        
        if orientation == 'v':
            self.add_text_bb(label2, x=x, y=y, align='c')

            y1 = y + h + padding
            x1 = x - hf/2
            self.add_rot_trans(image, x=x1, y=y1 + w, rotate=-90)
            self.add_frame(x=x1, y=y1, w=hf, h=w)
            y1 += w + h + padding
            self.add_text_bb(label1, x=x, y=y1, align='l')
        else:
            if align == 'c':
                x = x - cw / 2
                
            self.add_text(label1, x, y + h)
            x1 = (x + sw1 + padding)
            y1 = y + (h - hf) / 2
            self.add_trans(image, x=x1, y=y1)
            self.add_frame(x1, y1, w, h=hf)

            self.add_text(label2, x1 + w + padding, y + h)
            
    def add_num_colorbar(self,
                     x=0,
                     y=0,
                     w=160,
                     h=20,
                     name='bgy',
                     ticks=[-2, 0, 2],
                     ticklabels=['-2', '0', '2'],
                     lim=[-2, 2],
                     dir=svgplot.COLORBAR_DIR,
                     orientation='h',
                     padding=4,
                     align='c',
                     side='l',
                     inside=False,
                     showticks=True,
                     tickstroke=2):
        if ticklabels is None:
            ticklabels = ticks
        
        #file = '{}/{}_colorbar.png'.format(dir, name)
        file = f'{dir}/{name}_colorbar.png'
        
        print(file)
        
        w, h, image = self.base_image(file, w=w, h=h)
        

        if lim is None:
            lim = [ticks[0], ticks[len(ticks) - 1]]
            
        self.set_font_size(svgplot.FIGURE_FONT_SIZE)
        
        if orientation == 'v':
            yaxis = axis.Axis(lim=lim, w=w)
            self.add_rot_trans(image, x=x, y=y + w, rotate=-90)
            self.add_frame(x=x, y=y, w=h, h=w, stroke=2)
            
            x1 = x + h
            
            if not inside:
                x1 += padding - 3
            
            self.add_y_axis(axis=yaxis, 
                            x=x1, 
                            y=y+w, 
                            ticks=ticks, 
                            ticklabels=ticklabels, 
                            inside=inside,
                            side='r',
                            showline=False,
                            showticks=showticks,
                            tickstroke=tickstroke,
                            ticksize=5)
        else:
            if align == 'c':
                x = x - w / 2
                
            #x1 = x + sw1 / 2
            xaxis = axis.Axis(lim=lim, w=w)
            self.add_trans(image, x=x, y=y)
            self.add_frame(x, y, w, h=h, stroke=2)
            
            y1 = y + h
            
            if not inside:
                y1 += padding - 3
            
            self.add_x_axis(axis=xaxis, 
                            x=x, 
                            y=y1, 
                            ticks=ticks, 
                            ticklabels=ticklabels, 
                            inside=inside,
                            showline=False,
                            tickstroke=tickstroke,
                            showticks=showticks,
                            ticksize=5)
        
        self.set_font_size(svgplot.DEFAULT_FONT_SIZE)
        
    def add_num_colorbar_norm(self,
                          x=0,
                          y=0,
                          name='bgy',
                          dir=svgplot.COLORBAR_DIR,
                          orientation='h'):
        self.add_num_colorbar(x=x, 
                              y=y,
                              name=name, 
                              dir=dir,
                              lim=[0, 1],
                              ticks=[0, 0.5, 1], 
                              ticklabels=[0, 0.5, 1],
                              orientation=orientation)
    
    def add_num_colorbar_low(self,
                             x=0,
                             y=0,
                             name='viridis',
                             orientation='h',
                             dir=svgplot.COLORBAR_DIR):
        self.add_num_colorbar_z(x=x,
                              y=y,
                              name=name,
                              orientation=orientation, 
                              z=1.5,
                              dir=dir)
        
    def add_num_colorbar_z(self,
                             x=0,
                             y=0,
                             name='viridis',
                             align='c',
                             orientation='h',
                             z=1.5,
                             dir=svgplot.COLORBAR_DIR):
        self.add_num_colorbar(x=x,
                              y=y,
                              orientation=orientation, 
                              align=align,
                              side='r',
                              name=name, 
                              ticks=[-z, 0, z],
                              lim=[-z, z],
                              showticks=False,
                              ticklabels=[-z, 0, z])

    def add_norm_colorbar(self,
                          x=0,
                          y=0,
                          orientation='h',
                          name='viridis',
                          dir=svgplot.COLORBAR_DIR):
        """
        Add a 0 - 1 colorbar
        """
        #self.add_colorbar(x=x, 
        #                  y=y, 
        #                  w=w, 
        #                  name=name,
        #                  label1='0', 
        #                  label2='1', 
        #                  dir=dir)
        self.add_num_colorbar(x=x,
                              y=y,
                              orientation=orientation,
                              align='c',
                              side='r',
                              name=name,
                              ticks=[0, 1],
                              lim=[0, 1],
                              showticks=False,
                              ticklabels=[0, 1])

    def add_sep_clust_col(self,
                          name,
                          block,
                          x=0,
                          y=0,
                          w=180,
                          color=svgplot.COLOR_BLACK,
                          method='umap',
                          padding=20,
                          max_rows=5):
        start_x = x
        start_y = y

        if len(block) == 0:
            return (0, 0)

        cols = 2 if len(block) > max_rows else 1

        block_width = w * cols + padding * (cols - 1)

        self.add_heading(name,
                         x=x,
                         y=y,
                         w=block_width,
                         color=color,
                         bracket_offset=10,
                         show_bracket=True)

        y += padding  # + self.get_font_h()

        ht = 0

        for i in range(0, len(block)):
            item = block[i]

            group = item[0]
            cluster = item[1]

            f = svgplot.find_sep_clust_file(group, cluster)

            self.add_image(f, x=x, y=y, w=w)

            h = int(math.ceil(svgplot.scaled_image_h(f, w)))

            if i < max_rows:
                # max height will one full column, so stop here
                ht += h

            y += h + padding

            if i == max_rows - 1:
                y = start_y + svgplot.SEP_CLUST_LABEL_HEIGHT
                x += w + padding

        return (block_width, ht)

    def add_heading(self,
                    name,
                    x=0,
                    y=0,
                    w=0,
                    color=svgplot.COLOR_BLACK,
                    linespacing=10,
                    bracket_offset=10,
                    weight='normal',
                    show_bracket=False,
                    split=False,
                    stroke=svgplot.STROKE_SIZE):
        #th = self.get_font_h()

        if split:
            words = name.split(' ')
        else:
            words = [name]
        
        y2 = y - 0.5 * (self.get_font_h() + linespacing) * (len(words) - 1)
        
        for word in words:
            self.add_text_bb(word,
                             x=x,
                             y=y2, 
                             w=w,
                             color=color,
                             align='c',
                             weight=weight)
            y2 += self.get_font_h() + linespacing
            
        sw = 0
        
        for word in words:
            sw = max(sw, self.get_string_width(word))

        if show_bracket:
            y1 = y  # + (SEP_CLUST_LABEL_HEIGHT // 2)

            gap = (w - 2 * bracket_offset - sw) // 2 - 10

            x1 = x + bracket_offset
            x2 = x1 + gap

            if x2 - x1 > 20:
                self.add_line(x1=x1, y1=y1, x2=x2, y2=y1, color=color, stroke=stroke)
#                self.add_line(x1=x1, y1=y1, x2=x1, y2=y +
#                              svgplot.BRACKET_SIZE, color=color)

            x2 = x + w - bracket_offset
            x1 = x2 - gap - len(word) * 1.5  #+ 5

            if x2 - x1 > 20:
                self.add_line(x1=x1, y1=y1, x2=x2, y2=y1, color=color, stroke=stroke)
#                self.add_line(x1=x2, y1=y1, x2=x2, y2=y +
#                              svgplot.BRACKET_SIZE, color=color)
        n = (len(words) - 1) / 2
        
        return self.get_font_h() * (1 + n) + linespacing * n

    def add_vert_sep_cluster(self,
                             name,
                             format,
                             start_x=0,
                             start_y=0,
                             w=180,
                             color=svgplot.COLOR_BLACK,
                             method='umap',
                             padding=30,
                             dir='.',
                             max_rows=5):
        x = start_x

        files = svgplot.find_sep_clust_files(format, dir, method=method)
         
        if len(files) == 0:
            return (0, 0)

        th = self.get_font_h()

        cols = 2 if len(files) > max_rows else 1

        block_width = w * cols + padding * (cols - 1)
        
        self.add_heading(name, 
                         x=x, 
                         y=start_y, 
                         w=block_width, 
                         color=color, 
                         show_bracket=(cols > 1),
                         weight='normal')

#        bracket_width = block_width - 10
#        bracket_offset = (block_width - bracket_width) // 2
#
#        sw = self.get_string_width(name)
#
#        self.add_text_bb(name, x=x, y=start_y, w=block_width,
#                         color=color, align='c', weight=weight)
#
#        y1 = start_y  # + (SEP_CLUST_LABEL_HEIGHT // 2)
#
#        gap = (bracket_width - sw) // 2 - 5
#
#        x1 = x + bracket_offset
#        x2 = x1 + gap
#
#        if x2 - x1 > 5:
#            self.add_line(x1, y1, x2, y1, color=color)
#            self.add_line(x1, y1, x1, start_y +
#                          svgplot.BRACKET_SIZE, color=color)
#
#        x2 = x + block_width - bracket_offset
#        x1 = x2 - gap + 5
#
#        if x2 - x1 > 5:
#            self.add_line(x1, y1, x2, y1, color=color)
#            self.add_line(x2, y1, x2, start_y +
#                          svgplot.BRACKET_SIZE, color=color)

        y = start_y + svgplot.SEP_CLUST_LABEL_HEIGHT + padding

        ht = 0

        x = start_x

        for i in range(0, len(files)):
            f = files[i]

            self.add_image(f, x=x, y=y, w=w)

            h = int(math.ceil(svgplot.scaled_image_h(f, w)))

            if i < 6:
                # max height will one full column, so stop here
                ht += h

            y += h + padding

            if i == max_rows - 1:
                y = start_y + th
                x += w + padding

        return (block_width, ht + th + padding)

    def add_vert_sep_clusters(self,
                              name,
                              clusters,
                              start_x=0,
                              start_y=0,
                              w=180,
                              method='umap',
                              padding=30,
                              dir='.',
                              max_rows=6):

        dir = svgplot.find_sep_clust_dir(name)

        x = start_x
        y = start_y

        nw, nh = self.add_vert_sep_cluster('DZ',
                                           'dz',
                                           x,
                                           y,
                                           w,
                                           clusters.get_block_color(
                                               'DZ'),
                                           method=method,
                                           padding=padding,
                                           dir=dir,
                                           max_rows=max_rows)

        if nw > 0:
            x += nw + padding

        nw, nh = self.add_vert_sep_cluster('INT',
                                           'intermediate',
                                           x,
                                           y,
                                           w,
                                           clusters.get_block_color(
                                               'Int'),
                                           method=method,
                                           padding=padding,
                                           dir=dir,
                                           max_rows=max_rows)

        if nw > 0:
            x += nw + padding

        nw, nh = self.add_vert_sep_cluster('LZ',
                                           'lz',
                                           x,
                                           y,
                                           w,
                                           clusters.get_block_color(
                                               'LZ'),
                                           method=method,
                                           padding=padding,
                                           dir=dir,
                                           max_rows=max_rows)
        #if nw > 0:
        #    x += nw + padding
            
        #if nh > 0:
        y += nh + svgplot.SEP_CLUST_LABEL_HEIGHT + 2 * padding

        #h = print_vert_sep_cluster(svg, sample, 'Tr', 'transit', x, y, w, colormaps.rgba_to_RGB(colormaps.golds(0)))
        #y += h + SEP_CLUST_LABEL_HEIGHT

        
        nw, nh = self.add_vert_sep_cluster('PreM',
                                  'prem',
                                  x,
                                  y,
                                  w,
                                  clusters.get_block_color('PreM'),
                                  method=method,
                                  padding=padding,
                                  dir=dir,
                                  max_rows=max_rows)
        
        #x += w
        #y = start_y
        if nh > 0:
            y += nh + svgplot.SEP_CLUST_LABEL_HEIGHT + 2 * padding

        nw, nh = self.add_vert_sep_cluster('PBL',
                                           'pbl',
                                           x,
                                           y,
                                           w,
                                           clusters.get_block_color(
                                               'PBL'),
                                           method=method,
                                           padding=padding,
                                           dir=dir,
                                           max_rows=max_rows)

        return x + nw - start_x

    def add_sub_panel(self,
                      file,
                      x=0,
                      y=0,
                      w=svgplot.DEFAULT_IMAGE_SIZE,
                      h=None,
                      label=None,
                      sub_label=None,
                      label_color=svgplot.COLOR_BLACK,
                      labelxy=(0, 0),
                      padding=80,
                      color=svgplot.COLOR_BLACK,
                      shape='c',
                      frame=True):
        if h is None:
            h = w

        if frame:
            self.add_frame(x, y, w, h, padding=padding,
                           shape=shape, color='none', fill=svgplot.COLOR_WHITE)

        self.add_image(file, x=x, y=y, w=w)

        if label is not None:
            if sub_label is not None:
                self.add_title(label, sub_label, x=x, y=y+h +
                               self.get_font_h(), w=w, color=color)

            else:
                self.add_text(
                    label, x + labelxy[0], y + labelxy[1], color=label_color)

        if frame:
            self.add_frame(x, y, w, h, padding=padding,
                           color=color, shape=shape)

    def add_monocle(self, name, x=50, y=0, w=500):
        dir = svgplot.find_monocle_dir(name)
        file = svgplot.find_monocle_png(os.path.join(dir, 'trimmed'))

        self.add_image(file, x=x, y=y, w=w)

    def add_monocle_plot(self, name, x=0, y=0, w=500, offset=20):
        self.add_monocle(name, x=x+offset, y=y, w=w)
        self.add_axes(x=x, y=y+w+offset)

    def add_umap(self, sample, name, x=50, y=0, w=500, title=''):
        dir = svgplot.find_umap_dir(sample)
        file = svgplot.find_umap_png(os.path.join(dir, 'trimmed'), name)
        
        print(dir, file)
        
        return self.add_image(file, x=x, y=y, w=w, title=title, titleposition='top')

    def add_umap_plot(self, sample, name='trim', x=50, y=0, w=500, offset=20, title=''):
        w, h = self.add_umap(sample, name, x=x+offset, y=y, w=w, title=title)
        self.add_axes(labelx='UMAP 1', 
                      labely='UMAP 2', 
                      x=x, 
                      y=y+h+offset, 
                      size=svgplot.FIGURE_FONT_SIZE)


    def add_vert_sep_monocle_group(self,
                                   group,
                                   name,
                                   clusters,
                                   start_x=0,
                                   start_y=0,
                                   w=180,
                                   color=svgplot.COLOR_BLACK,
                                   padding=20,
                                   max_rows=3,
                                   weight='normal'):
        x = start_x
        
        ids = clusters.get_ids(name) #np.where(clusters['Display Id'].str.contains(name))[0]

        if ids.size == 0:
            return (0, 0)

        th = self.get_font_h()

        cols = ids.size // max_rows # if ids.size > max_rows else 1
        
        if ids.size % max_rows > 0:
            cols += 1

        block_width = w * cols + padding * (cols - 1)

        self.add_heading(name, x=x, y=start_y, w=block_width, color=color, show_bracket=(cols > 1))

#        bracket_width = block_width - 10
#        bracket_offset = (block_width - bracket_width) // 2
#
#        sw = self.get_string_width(name)
#
#        self.add_text_bb(name,
#                         x=x,
#                         y=start_y,
#                         w=block_width,
#                         color=color,
#                         align='c',
#                         weight=weight)
#
#        y1 = start_y
#
#        gap = (bracket_width - sw) // 2 - 5
#
#        x1 = x + bracket_offset
#        x2 = x1 + gap
#
#        if x2 - x1 > 5:
#            self.add_line(x1, y1, x2, y1, color=color)
#            self.add_line(x1, y1, x1, start_y +
#                          svgplot.BRACKET_SIZE, color=color)
#
#        x2 = x + block_width - bracket_offset
#        x1 = x2 - gap + 5
#
#        if x2 - x1 > 5:
#            self.add_line(x1, y1, x2, y1, color=color)
#            self.add_line(x2, y1, x2, start_y +
#                          svgplot.BRACKET_SIZE, color=color)

        y = start_y + th + padding

        ht = 0

        x = start_x

        for i in range(0, ids.size):
            id = ids[i]

            cluster = clusters.get_cluster(id)

            f = svgplot.find_sep_clust_file(group, cluster, type='monocle')

            self.add_image(f, x=x, y=y, w=w)

            h = int(math.ceil(svgplot.scaled_image_h(f, w)))

            if i < max_rows:
                # max height will one full column, so stop here
                ht += h

            y += h + padding

            if (i % max_rows) == max_rows - 1:
                y = start_y + th + padding
                x += w + padding

        return (block_width, ht + th + padding)

    def add_vert_sep_monocle(self,
                             group,
                             clusters,
                             x=0,
                             y=0,
                             w=150,
                             padding=10,
                             max_rows=3):
        start_x = x
        start_y = y
        
        x = start_x + 202

        nw, nh = self.add_vert_sep_monocle_group(group,
                                                 'DZ',
                                                 clusters,
                                                 x,
                                                 y,
                                                 w,
                                                 color=clusters.get_block_color('DZ'),
                                                 padding=padding,
                                                 max_rows=1)

        #x += nw + 4 * padding
        x = start_x + 50
        y += nh + 4 * padding
        #x += nw + 6 * padding

        nw, nh = self.add_vert_sep_monocle_group(group,
                                                 'INT',
                                                 clusters,
                                                 x,
                                                 y,
                                                 w,
                                                 color=clusters.get_block_color('Int'),
                                                 padding=padding,
                                                 max_rows=1)

        #x += nw + padding
        x = start_x
        y += nh + 4 * padding

        nw, nh = self.add_vert_sep_monocle_group(group,
                                                 'LZ',
                                                 clusters,
                                                 x,
                                                 y,
                                                 w,
                                                 color=clusters.get_block_color('LZ'),
                                                 padding=padding,
                                                 max_rows=1)
        #y += nh + SEP_CLUST_LABEL_HEIGHT

        x += nw + 6 * padding

        #h = print_vert_sep_cluster(svg, sample, 'Tr', 'transit', x, y, w, colormaps.rgba_to_RGB(colormaps.golds(0)))
        #y += h + SEP_CLUST_LABEL_HEIGHT

        nw, nh = self.add_vert_sep_monocle_group(group,
                                        'PreM',
                                        clusters,
                                        x,
                                        y,
                                        w,
                                        color=clusters.get_block_color('PreM'),
                                        padding=padding,
                                        max_rows=1)



        
        #y += nh + svgplot.SEP_CLUST_LABEL_HEIGHT + padding
        x += nw + 6 * padding

        nw, nh = self.add_vert_sep_monocle_group(group,
                                         'PBL',
                                         clusters,
                                         x,
                                         y,
                                         w,
                                         color=clusters.get_block_color('PBL'),
                                         padding=padding,
                                         max_rows=1)

        return x + nw - start_x






    def add_clusters(self, 
                     name, 
                     clusters, 
                     x=0, 
                     y=0, 
                     w=150,
                     padding=10,
                     hspace=10,
                     vspace=10,
                     max_rows=4,
                     remap={},
                     layout={},
                     ignore={},
                     ext_labels={},
                     split={},
                     label=True,
                     add_heading=True,
                     dir=None,
                     stroke=svgplot.STROKE_SIZE):
        startx = x
        starty = y
        blockx = startx - w
        
        if dir is None:
            dir = svgplot.find_sep_clust_dir(name)
        
        groups = []
        
        cluster_map = collections.defaultdict(list)
        
        for i in range(0, clusters.size):
            id = clusters.get_id(i)
             
            #if isinstance(remap, dict) and id in remap:
            #    group = remap[id]
            #else:
    
            group = clusters.get_short_group(id) #get_short_group(id)
            
            if id in ignore or group in ignore:
                continue
            
            if group not in cluster_map:
                color = clusters.get_block_color(group) #id) #cluster_colors.get_group(id)
                groups.append([group, color])
                
            cluster_map[group].append([clusters.get_cluster(id), id, clusters.get_color(id)])
        
    
        lh = self.get_font_h()
        hh = 0
        
        for i in range(0, len(groups)):
            group = groups[i]
            
            row = 0
              
            if isinstance(remap, dict) and group[0] in remap:
                name = remap[group[0]]
            else:
                name = group[0]
                
            if group[0] in layout and layout[group[0]] == 1:
                y = starty
                
                blockx += w
                
                if i > 0:
                    blockx += padding
                    
                row = 0
                
            x = blockx
            
            # spacing above secondary blocks
            if y > starty:
                if (name in split):
                    words = name.split(' ')
                else:
                    words = [name]
                    
                y += lh * len(words)

                
            cols = len(cluster_map[group[0]]) // max_rows + len(cluster_map[group[0]]) % max_rows
            
            if add_heading:
                if len(cluster_map[group[0]]) > max_rows:
                    hh = self.add_heading(name, 
                                     x=x, 
                                     y=y, 
                                     w=cols*w +(cols-1)*padding, 
                                     color=group[1], 
                                     show_bracket=True, 
                                     split=(name in split),
                                     stroke=stroke)
                else:
                    hh = self.add_heading(name, 
                                     x=x, 
                                     y=y, 
                                     w=w, 
                                     color=group[1], 
                                     split=(name in split),
                                     stroke=stroke)
                
            #if name in split:
            #    y += lh
            
            y += lh + vspace # padding #hh
            
            files = svgplot.find_sep_clust_files(group[0].lower().replace(' ', ''), dir, method='umap')
            
            for cluster in cluster_map[group[0]]:
                for file in files:
                    if 'c{}_'.format(cluster[0]) in file:
                        self.add_image(file, x=x, y=y, w=w)
                        
                        break
                y += w + lh
                
                if label:
                    if isinstance(remap, dict) and cluster[1] in remap:
                        name = remap[cluster[1]]
                    else:
                        name = cluster[1]
                        
                    if name in ext_labels:
                        name = name + ' ' + ext_labels[name]
                
                    self.add_text_bb(name, 
                                     color=cluster[2], 
                                     x=x,
                                     y=y,
                                     w=w, 
                                     align='c')
                    
                    y += lh + vspace #padding
                
                row += 1
                
                # only create new column if
                if row % max_rows  == 0 and row < len(cluster_map[group[0]]):
                    y = starty + lh + vspace #hh # * 1.5
                    
                    #if name in split:
                    #    y += lh
                    
                    #row = 0
                    blockx += w + padding
                    x = blockx
                    
                    
    def add_gene_group_exp(self,
                           name,
                           gene_groups,
                           x=0,
                           y=0,
                           w=200,
                           hspace=10,
                           vspace=10,
                           colormap='bgy',
                           max_cols=3,
                           dir=None):
        startx = x
        starty = y

        if dir is None:
            dir = svgplot.find_gene_exp_dir(name, colormap=colormap)

        for i in range(0, len(gene_groups)):
            gg = gene_groups[i]

            y = starty

            if i > max_cols:
                x = startx
                y += w + vspace

            self.add_heading(gg[0], x=x, y=y, color=gg[2], w=w)

            y += 1.5 * self.get_font_h()

            #svgplot.add_frame(x, y, EXP_SIZE, libsvgplot.LABEL_HEIGHT);

            maxw = 0

            for gene in gg[1]:
                print(gene)
                file = svgplot.find_exp_file(gene, dir)

                w, h = self.add_image(file, x=x, y=y, w=w)

                maxw = max(w, maxw)

                y += h + self.get_font_h()

                self.add_text_bb(gene, x=x, y=y, w=w, align='c')

                y += self.get_font_h() + vspace

            x += maxw + hspace
