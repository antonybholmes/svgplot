# -*- coding: utf-8 -*-
"""
Created on Thu Apr  1 17:47:24 2021

@author: Antony
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 09:36:28 2019

@author: antony
"""
import collections
import re
import numpy as np
import matplotlib
import yaml
import pandas as pd
import itertools
import random

from . import core
from . import svgfigureheatmap
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist
from scipy.spatial.distance import squareform

#MUTATION_SCORE_MAP = {'n/a':0, 'MISSENSE':3, 'TRUNC':2, 'INFRAME':1}
MUTATION_SCORE_MAP = {'n/a':0, 'TRUNC':1, 'MISSENSE':1, 'INFRAME':1}

MUTATION_INDEX_MAP = {'n/a':0, 'MISSENSE':3, 'TRUNC':2, 'INFRAME':1}

MUTATION_CMAP = matplotlib.colors.ListedColormap(['#e6e6e6', '#996633', '#000000', '#009933'])

LEGEND_SIZE = 20

def uniq_in_order(items):
    a = np.array(items)
    _, idx = np.unique(a, return_index=True)
    return a[np.sort(idx)]

def perm_sort(table):
    mut_cols = np.where(table.sum(axis=0) > 0)[0]
    no_mut_cols = np.where(table.sum(axis=0) == 0)[0]
    
    mut_table = table[:, mut_cols]
    
    indices = list(range(0, mut_table.shape[1]))
    
    max_s = 0
    max_idx = []
    
    pc = 0
    
    print(mut_table.shape)
    
    for idx in itertools.permutations(indices):
        #print(idx)
        table_perm = mut_table[:, idx]
        
        s = 0
        
        x1 = -1
        x2 = -1
        
        for r in range(0, table_perm.shape[0]):
            max_l = 0
            
            for c in range(0, table_perm.shape[1]):
                v = table_perm[r, c]
            
                if v > 0:
                    if x1 == -1:
                        x1 = c
                    
                    x2 = c
                else:
                    if x1 != -1:
                        l = x2 - x1 + 1
                        
                        if l > max_l:
                            max_l = l
        
                        x1 = -1
                        x2 = -1
            
            #print(r, max_l)
            s += max_l
            
        if s > max_s:
            max_idx = idx
            max_s = s
            
        pc += 1
        
        if pc % 10000 == 0:
            print('perm', pc, max_s)
            #break
    
    max_idx = np.array(max_idx)
    
    perm_idx = np.concatenate([mut_cols[max_idx], no_mut_cols])
    
    return perm_idx


def measure_longest_run(row_data):
    idx = np.where(row_data > 0)[0]
    # idx.sort()
    # max_run = 0
    # s = 0
    # i = 0
    
    # run_length = 0
    # runs = 0
    
    #for i in range(0, idx.size):
        # if i > 1 and idx[i] - idx[i - 1] > 1:
        #     run = i - s
            
        #     if run > 1:
        #         #scale by distance to start so closer to left = better
        #         run_length += run * (1 - (i + 1) / row_data.size)
        #         runs += 1
            
        #     if run > max_run:
        #         max_run = run
            
        #     s = i
    
    # want max run but expressed so longer = smaller score hence return
    #
    
    #print(max_run)
    
    return idx.sum() #row_data.size - run_length / runs if runs > 0 else 0


def measure_config(table, weights):
    s = 0
    
    for row in range(0, table.shape[0]):
        s += measure_longest_run(table[row, :])
        
        # idx = np.where(table[row, :] > 0)[0]
        
        # if idx.size > 0:
        #     m = idx.min()
        #     l = idx.max() - m
        #     #s += (m + l) * weights[row]
        #     s += (l) * weights[row]
        
    return s

def metropolis_hasting(table, sampling=100000):
    mut_cols = np.where(table.sum(axis=0) > 0)[0]
    no_mut_cols = np.where(table.sum(axis=0) == 0)[0]
    
    mut_table = table[:, mut_cols]
    
    weights = np.ones(table.shape[0]) #np.array(list(range(table.shape[0], 0, -1))) / table.shape[0]

    ref_score = measure_config(table, weights=weights)
    
    max_score = ref_score
    
    n = mut_table.shape[1] - 1
    
    p = pdist(np.transpose(mut_table), metric='euclidean')
    sqp=squareform(p)
    
    cols = list(range(0, mut_table.shape[1]))
    
    pc = 0
    
    for s in range(0, sampling):
        for i in range(0, n):
            x1 = cols[i]
            x2 = cols[i + 1]
           
            #x1 = random.randint(0, n)
            #x2 = random.randint(0, n)
            
            #if x1 == x2:
            #    continue
            
            # measure if dist less with swap
            
            d1 = 0
            
            if x1 > 0:
                d1 += sqp[x1, x1 - 1]
            #if x1 < n:
            #    d1 += sqp[x1, x1 + 1]
            #if x2 > 0:
            #    d1 += sqp[x2, x2 - 1]
            if x2 < n:
                d1 += sqp[x2, x2 + 1]
                
            # swap
            
            d2 = 0
            
            if x1 > 0:
                d2 += sqp[x2, x1 - 1]
            #if x1 < n:
            #    d2 += sqp[x2, x1 + 1]
            #if x2 > 0:
            #    d2 += sqp[x1, x2 - 1]
            if x2 < n:
                d2 += sqp[x1, x2 + 1]
            
            
            
            if d2 <= d1:
                #print(x1, x2, d1, d2, pc)
                tmp = cols[x1]
                cols[x1] = cols[x2]
                cols[x2] = tmp
        
        # # swap columns
        # col_test = cols.copy()
        # tmp = col_test[x1]
        # col_test[x1] = col_test[x2]
        # col_test[x2] = tmp
        
        # mut_table_test = mut_table[:, col_test]
        
        # score = measure_config(mut_table_test, weights)
        
        
        
        # if score < max_score:
        #     print(s, score, max_score)
        #     cols = col_test
        #     max_score = score

        pc += 1
        
        if pc % 10000 == 0:
            print('sample', pc)
    
    perm_idx = np.concatenate([mut_cols[cols], no_mut_cols])
    
    return perm_idx

def sort(table, 
         row,
         offset,
         indices, 
         mut_cols,
         mut_rank_table,
         used_table,
         isanchor):
    """

    Parameters
    ----------
    table : pandas.DataFrame
        2d table indicating mutations for a given gene (row) and sample (col).
    row : TYPE
        DESCRIPTION.
    indices : TYPE
        DESCRIPTION.
    mut_cols : np.array
        1d array indicating if column has zero 1, or more mutations in the column.
    mut_rank_table : np.array
        DESCRIPTION.
    used_table : TYPE
        DESCRIPTION.
    isanchor : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    #base case
    if indices.size < 2 or row == table.shape[0]:
        return indices
    
    v = table.iloc[row, :].values
    
    ret = []
    
    # isolate block of samples of interest, but the sort order is determined
    # by values in the next most mutated row and so on recursively until
    # there is nothing to sort. Thus missense will be preferrentially
    # bunched together at the top left of the plot and other combinations
    # will spread along the diagnonal
    
    #used_indices = np.intersect1d(np.where(mut_cols > 0)[0], indices)
    single_indices = np.intersect1d(np.where(mut_cols == 1)[0], indices)
    mult_indices = np.intersect1d(np.where(mut_cols == 2)[0], indices)

    idx_trunc = sort(table, 
                     row + 1,
                     offset,
                     np.intersect1d(np.where(v == 'TRUNC')[0], single_indices),
                     mut_cols,
                     mut_rank_table,
                     used_table,
                     False)
    
    idx_trunc_miss = sort(table, 
                          row + 1,
                          offset,
                          np.intersect1d(np.where(v == 'MISSENSE,TRUNC')[0], single_indices), 
                          mut_cols,
                          mut_rank_table,
                          used_table,
                          False)
    
    idx_miss = sort(table, 
                    row + 1,
                    offset,
                    np.intersect1d(np.where(v == 'MISSENSE')[0], single_indices), 
                    mut_cols,
                    mut_rank_table,
                    used_table,
                    False)
    
    idx_inframe = sort(table, 
                       row + 1,
                       offset,
                       np.intersect1d(np.where(v == 'INFRAME')[0], single_indices),
                       mut_cols,
                       mut_rank_table,
                       used_table,
                       False)
    
    idx_miss_inframe = sort(table, 
                          row + 1,
                          offset,
                          np.intersect1d(np.where(v == 'INFRAME,MISSENSE')[0], single_indices), 
                          mut_cols,
                          mut_rank_table,
                          used_table,
                          False)
    
    idx_trunc_inframe = sort(table, 
                          row + 1,
                          offset,
                          np.intersect1d(np.where(v == 'INFRAME,TRUNC')[0], single_indices), 
                          mut_cols,
                          mut_rank_table,
                          used_table,
                          False)
    
    
    idx_used = np.intersect1d(np.where(v != 'n/a')[0], indices)
    idx_mult = np.intersect1d(idx_used, mult_indices)
    

    # for each idx mult, for each row below, count how many children are
    # left or right and stack it in the clostest
    
    left_mode = False
    
    if idx_mult.size > 0:
        # score them by number of mutations in the column
        idx_mult_scores = mut_rank_table[row:, idx_mult].sum(axis=0)
        
        if row == 1:
            print('ha', mut_rank_table[row:, idx_mult])
            print('hmm', idx_mult_scores)
        idx_mult = idx_mult[np.argsort(idx_mult_scores)]
        
        # get indices of rows where children are
        idx_children = np.where(mut_rank_table[(row+1):, idx_mult].sum(axis=1) > 0)[0]
        
        idx_children += 1 + row
        
        if row == 1:
            print('id chil',idx_children)
            
            print(used_table[idx_children, :])
        
        # see if positions already used on row to left of where we are
        idx_left = np.where(used_table[idx_children, :].sum(axis=1) > 0)[0]
        
        left_mode = idx_left.size > 0
        
    if row == 1:
        print('mode', row, left_mode, idx_mult)
        
    if left_mode:
        #idx_trunc += idx_mult.size
        #idx_trunc_miss += idx_mult.size
        #idx_miss += idx_mult.size
        #idx_inframe += idx_mult.size
        
        # add at beginning but reverse sort
        ret.append(idx_mult[::-1])
    
    
    
    ret.append(idx_trunc)
    ret.append(idx_trunc_miss)
    ret.append(idx_trunc_inframe)
    ret.append(idx_miss)
    ret.append(idx_miss_inframe)
    ret.append(idx_inframe)
    
    if not left_mode:
        ret.append(idx_mult)
        
    idx_all_mut = np.concatenate([idx_trunc, idx_trunc_miss, idx_miss, idx_inframe])
    
    used_table[row, idx_all_mut] = 1
    
    if idx_mult.size > 0:
        # find used rows
        idx_children = np.where(mut_rank_table[row:, idx_mult].sum(axis=1) > 0)[0]
        idx_children += row
        
        print(row, idx_children, mut_rank_table[row:, idx_mult].shape)
        
        if left_mode:
            used_table[idx_children, offset:(offset+idx_mult.size)] = 1
        else:
            m = offset+idx_used.size
            used_table[idx_children, m-idx_mult.size:m] = 1
    
    idx_na = sort(table, 
                  row + 1,
                  offset + idx_used.size,
                  np.intersect1d(np.where(v == 'n/a'), indices),
                  mut_cols,
                  mut_rank_table,
                  used_table,
                  isanchor)
    
    ret.append(idx_na)
    
    return np.concatenate(ret)
    
    # # see if row contains mutations not covered here
    # idx_row = np.where(v != 'n/a')[0]
    
    # # if there is block of mutations in the unprocessed right half, try to
    # # push blocks rightwards by processing n/a first
    # # test whether there is an index in row greater than the max index in
    # # the block of mutations to indicate if mutation has siblings that it
    # # would be aesthetically pleasing to try and keep together where possible
    # right_shift = (not isanchor) and idx_all_mut.size < idx_row.size #np.intersect1d(idx_row, idx_all_mut).size < idx_row.size
    
    # if row == 0 or row == 1:
    #     print(row, right_shift, idx_all_mut, idx_row)
    
    # if right_shift:
    #     #idx = np.intersect1d(np.where(v == 'n/a'), indices)
    #     ret.append(sort(table, row + 1, np.intersect1d(np.where(v == 'n/a'), indices), isanchor))
        
    # ret.append(idx_trunc)
    # ret.append(idx_trunc_miss)
    # ret.append(idx_miss)
    # ret.append(idx_inframe)
    
    #idx = np.intersect1d(np.where((v == 'MISSENSE') | (v == 'TRUNC') | (v == 'INFRAME'))[0], indices)
    #ret.append(sort(table, row + 1, idx))
    
    
    
    #idx = np.intersect1d(np.where(v != 'n/a')[0], indices)
    #ret.append(sort(table, row + 1, idx))
    
    
    #if not right_shift:
        #idx = np.intersect1d(np.where(v == 'n/a'), indices)
    #    ret.append(sort(table, row + 1, np.intersect1d(np.where(v == 'n/a'), indices), isanchor))
    
    #return np.concatenate(ret)

class SVGFigureMutationHeatmap(svgfigureheatmap.SVGFigureHeatmap):
    def __init__(self,
                 file,
                 size=('11in', '8.5in'),  # size=('279mm', '216mm'),
                 view=(2790, 2160),
                 grid=(12, 12),
                 subgrid=(12, 12),
                 border=50):
        super().__init__(file,
                         size=size,
                         view=view,
                         grid=grid,
                         subgrid=subgrid,
                         border=border)
        
    def add_mutation_heatmap(self,
                    name,
                    df_maf, 
                    df_labels, 
                    df_colors,
                    df_samples,
                    genes,
                    df_color_table,
                    x=0, 
                    y=0, 
                    cell=[14, 34],
                    lim=[0, 3],
                    gap=[10, 0],
                    cmap=MUTATION_CMAP,
                    gridcolor='white',
                    titleoffset=[15, 48],
                    labeloffset=20,
                    showgrid=True,
                    showframe=True,
                    extra_annotations=[]):
    
        mapper = matplotlib.cm.ScalarMappable(norm=matplotlib.colors.Normalize(vmin=lim[0], vmax=lim[1]), 
                                              cmap=cmap)
        
        all_genes = np.concatenate(genes)
        
        print(all_genes)
        
        #genes = uniq_in_order(genes)
        
        tables = []
        score_tables = []
        
        for sample in df_samples:
            print(sample)
            
            # find the idx of the samples that match
            clusters = []
            
            for match in sample['matches']:
                idx = np.where(df_colors['Display Id'] == match)[0]
                if idx.size > 0:
                    idx = idx[0]
                    cluster = df_colors['Cluster'].values[idx]
                    clusters.append(cluster)
            
            clusters = np.array(clusters)
            
            # idx of barcodes
            idx = np.where(df_labels.iloc[:].isin(clusters))[0]
            
            samples = df_labels.index[idx].values
            
            df = pd.DataFrame(np.full((all_genes.size, samples.size), 'n/a', dtype=object), 
                              index=all_genes, 
                              columns=samples)
            
            for i in range(0, all_genes.size):
                for j in range(0, samples.size):
                    
                    idx = np.where((df_maf['SUBJECT_NAME'] == samples[j]) & (df_maf['GENE SYMBOL'] == all_genes[i]))[0]
                    if idx.size > 0:
                        mut_types = df_maf['MUTATION_TYPE'].values[idx]
                        #print(samples[j], genes[i], mut_types)
                        df.iloc[i, j] = ','.join(sorted(set(mut_types))) #MUTATION_INDEX_MAP[mut_types[0]]
            
            tables.append(df)
            
            df.to_csv('{}_{}_mut_table.txt'.format(name, sample['name']), sep='\t', header=True, index=True)
        
        # sort tables
        
        for i in range(0, len(df_samples)):        
            table = tables[i]
            
            score_table = np.zeros(table.shape, dtype=int)
            
            for k in range(0, table.shape[1]):
                s = 0
                
                for j in range(0, table.shape[0]):
                    v = table.iloc[j, k]
                    
                    if v != 'n/a':
                        mut_types = np.array(v.split(','))
                        
                        # missense has highest score followed by truncation
                        # and then inframe. Multiple mutations sum so get
                        # lowest score and pushed to right
                        m = np.mean([MUTATION_SCORE_MAP[mut_type] for mut_type in mut_types])
                        #s = min(np.sum([MUTATION_INDEX_MAP[mut_type] for mut_type in mut_types]), 1)
                        #m = s #1 / pow(2, s - 1) if s > 0 else 0
                    else:
                        m = 0
                        
                    # basically score 1 if any mutation, else 0
                    #m = 1 / pow(2, mut_types.size) #min(np.max([MUTATION_INDEX_MAP[mut_type] for mut_type in mut_types]), 1) # mean
                    
                    # scale counts by rank to keep upper rows closer to left
                    #m /= (j + 1)
                    
                    score_table[j, k] = m
                    
                    s += m
             
            # score only with genes in upper or lower half
            if i == 0:
                #score_table[-genes[1].size:, :] = 0
                row_rank = np.array(list(range(0, score_table.shape[0])))
            else:
                #score_table[0:genes[0].size, :] = 0
                row_rank = np.concatenate([np.array(list(range(genes[0].size, score_table.shape[0]))), np.array(list(range(0, genes[0].size)))])
                    
            score_tables.append(score_table)
                
            # rank by highest mutations in a row
            #row_rank = np.argsort(np.sum(score_table, axis=1))[::-1]
            
            score_table_row_rank = score_table[row_rank, :] #* rank
            
            rank_table = table.iloc[row_rank, :].copy()
            
            mut_table = np.zeros(rank_table.shape, dtype=int)
            mut_table[rank_table != 'n/a'] = 1
            
            mut_cols = np.zeros(mut_table.shape[1])
            mut_cols[np.where(mut_table.sum(axis=0) == 1)[0]] = 1
            mut_cols[np.where(mut_table.sum(axis=0) > 1)[0]] = 2
            
            print('sd', mut_cols)
            
            # score rows based on table rather than best rank so that visually
            # genes in adjacent rows are more likely to stay together
            v = np.array(list(range(rank_table.shape[0], 0, -1))) #[1000 / pow(10, x) for x in range(0, rank_table.shape[0])] #range(0, rank_table.shape[0])] #row_rank] #range(0,rank_table.shape[0])]
            mut_rank_table = np.transpose(np.array([v] * rank_table.shape[1])) #np.transpose(np.array([list(range(rank_table.shape[0], 0, -1))] * rank_table.shape[1]))
            mut_rank_table[rank_table == 'n/a'] = 0
            
            # for k in range(0, table.shape[1]):
            #     for j in range(0, table.shape[0]):
            #         v = table.iloc[j, k]
                    
            #         if v != 'n/a':
            #             mut_types = np.array(v.split(','))
            #             m = np.mean([MUTATION_SCORE_MAP[mut_type] for mut_type in mut_types])
            #         else:
            #             m = 0
                        
            #         mut_rank_table[j, k] *= m
            
            
            mut_rank_table[rank_table == 'n/a'] = 0
            #print(mut_rank_table)
            
            used_table = np.zeros(mut_rank_table.shape, dtype=int)
            
            print('sort', mut_rank_table.shape, row_rank.size, score_table.shape)
            # col_rank = sort(rank_table, 
            #                 0,
            #                 0,
            #                 np.array(list(range(0, rank_table.shape[1]))),
            #                 mut_cols,
            #                 mut_rank_table,
            #                 used_table,
            #                 True)
            
            col_rank = metropolis_hasting(score_table_row_rank)
            
            #col_rank = perm_sort(score_table)
    
            
            # scale rows by 2^rank. This ensures the sort is biased towards
            # rows with highest total mutations
            
            # pc = pow(10, score_table_row_rank.shape[0] - 1)
            # print(pc, score_table_row_rank.shape[1], )
            # for r in range(0, score_table_row_rank.shape[0]):
            #     pc2 = pc / 10
            #     pcr = pc - pc2
                
            #     score_table_row_rank[r, :] = score_table_row_rank[r, :] * pc #pow(2, r) #(r + 1)
            #     print('fdsd', r, pc, pc2, pcr, score_table_row_rank[r, :].sum(), score_table_row_rank.shape[1], (score_table_row_rank[r, :] / score_table_row_rank.shape[1]).sum())
            #     pc = pc2
            
            # print('cols', score_table_row_rank.sum(axis=1))
            
            # col_rank = np.argsort(np.sum(score_table_row_rank, axis=0))[::-1]
            
            print('row rank', row_rank)
            
            
            
            # p = pdist(score_table, metric='euclidean')
            # Z = linkage(p, method='average')
            # dn = dendrogram(Z, no_plot=True)
            # row_order = np.array(dn['leaves'])
            
            # keep only cols with mutations
            
            mut_cols = np.where(score_table_row_rank.sum(axis=0) > 0)[0]
            no_mut_cols = np.where(score_table_row_rank.sum(axis=0) == 0)[0]
            mut_table = score_table_row_rank[:, mut_cols]
            
            for r in range(0, mut_table.shape[0]):
                mut_table[r, :] = mut_table[r, :] * v[r]
            
            print(mut_table.shape)
            p = pdist(np.transpose(mut_table), metric='euclidean')
            Z = linkage(p, method='single', optimal_ordering=True)
            dn = dendrogram(Z, no_plot=True)
            idx = np.array(dn['leaves'])
            #col_rank = np.concatenate([mut_cols[idx], no_mut_cols])
            
            tables[i] = table.iloc[:, col_rank]
            score_tables[i] = score_table_row_rank[:, col_rank]
                 
            #idx = np.argsort(sums)[::-1]
            #tables[i] = table.iloc[:, idx]
            
            #tables[i] = table.iloc[:, col_order]
            
            
        for i in range(0, len(df_samples)):        
            table = tables[i]
            
            hx = x
            hy = y
            
            w = cell[0] * table.shape[1]
            h = cell[1] * table.shape[0]
            
            for j in range(0, i):
                hx += tables[j].shape[1] * cell[0] + gap[0]
            
            
            color = core.rgbatohex(mapper.to_rgba(MUTATION_INDEX_MAP['n/a']))
            self.add_rect(hx, hy, w, h, fill=color)
            
            #print(i, x, hx, len(tables))
            
            # labels and annoations
            
            hy1 = hy - titleoffset[0]
            
            bh = titleoffset[1] * 0.7
            bo = (titleoffset[1] - bh) / 2
            
            for annotation in extra_annotations:
                hx1 = hx
                hy2 = hy1 - titleoffset[1] 
                
                cx1 = None
                cx2 = None
                
                for si in range(0, table.shape[1]):
                    sample = table.columns[si]
      
                    if sample in annotation["samples"]:
                        color = annotation["samples"][sample][1]
                        
                        cx2 = [hx1, color]
                        
                        if cx1 is None:
                            cx1 = cx2
                        
                        if (cx2[1] != cx1[1]):
                            self.add_rect(cx1[0], hy2 + bo, cx2[0] - cx1[0], bh, fill=cx1[1])
                            cx1 = cx2
                    else:
                        cx1 = None
                        cx2 = None
                        
                    hx1 += cell[0]
                
                # add last remaining bar
                self.add_rect(cx1[0], hy2 + bo, hx1 - cx1[0], bh, fill=cx1[1])
                
                self.add_frame(x=hx, 
                               y=hy2 + bo, 
                               w=w, 
                               h=bh,
                               stroke=2)
                
                if i == len(df_samples) - 1:
                    hx1 += labeloffset
                    self.add_text_bb(annotation['name'], x=hx1, y=hy1-titleoffset[1]/2)
                
                hy1 -= titleoffset[1] + titleoffset[0]
            
            if titleoffset[0] > -1:
                idx = np.where(df_colors['Display Id'] == df_samples[i]['matches'][0])[0][0]
                colorId = df_colors['Color Id'].values[idx]
                print(colorId)
                color = df_color_table['Color'].values[np.where(df_color_table['Cluster Name'] == colorId)[0][0]]
                #color = core.rgbatohex(color)
                
                self.add_rect(hx, hy1 - titleoffset[1], table.shape[1] * cell[0], titleoffset[1], fill=color)
                
                self.add_text_bb(df_samples[i]['name'], align='c', x=hx, y=hy1-titleoffset[1]/2, w=table.shape[1] * cell[0], color='white')
                
            for j in range(0, table.shape[0]):
                hx1 = hx
                
                for k in range(0, table.shape[1]):
                    #print(table.shape, j, k, df_samples[i]['name'])
                    v = table.iloc[j, k]
                    
                    if v != 'n/a':
                        mut_types = np.array(v.split(','))
                        mut_types = mut_types[0:min(len(mut_types), 2)]
                        
                        color = core.rgbatohex(mapper.to_rgba(MUTATION_INDEX_MAP[mut_types[0]]))
                        self.add_rect(hx1, hy, cell[0], cell[1], fill=color)
                        
                        if len(mut_types) > 1:
                            color = core.rgbatohex(mapper.to_rgba(MUTATION_INDEX_MAP[mut_types[1]]))
                            #self.add_lr_triangle(hx1, hy, cell[0], cell[1], fill=color)
     
                            h = cell[1] / mut_types.size
                            #hx2 = hx1
                            hy2 = hy + h
                            
                            #for mut_type in mut_types:
                            #    color = core.rgbatohex(mapper.to_rgba(MUTATION_INDEX_MAP[mut_type]))
                            
                            self.add_rect(hx1, hy, cell[0], h, fill=color)
                            hy2 += h
                        
                    hx1 += cell[0]
            
                hy += cell[1]
            
            w = cell[0] * table.shape[1]
            h = cell[1] * table.shape[0]
            
            if showgrid:
                self.add_grid(x=hx, 
                              y=y, 
                              w=w, 
                              h=h, 
                              rows=table.shape[0], 
                              cols=table.shape[1], 
                              color=gridcolor,
                              stroke=2)
            
            if showframe:
                self.add_frame(x=hx, y=y, w=w, h=h, stroke=2)
        
        if labeloffset > -1:
            hx += w + labeloffset
            hy = y + cell[1] / 2
            
            for gene in genes[0]:
                self.add_text_bb(gene, 
                              x=hx, 
                              y=hy,
                              color='#ff9900')
                hy += cell[1]
                
            for gene in genes[1]:
                self.add_text_bb(gene, 
                              x=hx, 
                              y=hy,
                              color='#6600cc')
                hy += cell[1]
            
        
        return score_tables
    
    
    def add_mutation_legend(self, 
                            x=0, 
                            y=0, 
                            cell=[30, 30],
                            lim=[0, 3],
                            cmap=MUTATION_CMAP):
        mapper = matplotlib.cm.ScalarMappable(norm=matplotlib.colors.Normalize(vmin=lim[0], vmax=lim[1]), 
                                              cmap=cmap)
        
        hx = x
        hy = y
        
        color = core.rgbatohex(mapper.to_rgba(MUTATION_INDEX_MAP['MISSENSE']))
        self.add_bullet('Missense mutation', color=color, shape='s')
        self.inc(y=40)
        color = core.rgbatohex(mapper.to_rgba(MUTATION_INDEX_MAP['TRUNC']))
        self.add_bullet('Truncating mutation', color=color, shape='s')
        self.inc(y=40)
        color = core.rgbatohex(mapper.to_rgba(MUTATION_INDEX_MAP['INFRAME']))
        self.add_bullet('Inframe ins/del', color=color, shape='s')
        self.inc(y=80)
        
        
        # color = core.rgbatohex(mapper.to_rgba(MUTATION_INDEX_MAP['MISSENSE']))
        # self.add_rect(hx, hy, LEGEND_SIZE, LEGEND_SIZE, fill=color)
        # #self.add_rect(hx, hy, LEGEND_SIZE, LEGEND_SIZE, color='black', stroke=2)
        # self.add_text_bb('Missense mutation', x=hx+2*LEGEND_SIZE, y=hy+LEGEND_SIZE/2, color=color)
        
        # hy += 40
        
        # color = core.rgbatohex(mapper.to_rgba(MUTATION_INDEX_MAP['TRUNC']))
        # self.add_rect(hx, hy, LEGEND_SIZE, LEGEND_SIZE, fill=color)
        # #self.add_rect(hx, hy, LEGEND_SIZE, LEGEND_SIZE, color='black', stroke=2)
        # self.add_text_bb('Truncating mutation', x=hx+2*LEGEND_SIZE, y=hy+LEGEND_SIZE/2, color=color)
        
        # hy += 40
        
        # color = core.rgbatohex(mapper.to_rgba(MUTATION_INDEX_MAP['INFRAME']))
        # self.add_rect(hx, hy, LEGEND_SIZE, LEGEND_SIZE, fill=color)
        # #self.add_rect(hx, hy, LEGEND_SIZE, LEGEND_SIZE, color='black', stroke=2)
        # self.add_text_bb('Inframe ins/del', x=hx+2*LEGEND_SIZE, y=hy+LEGEND_SIZE/2, color=color)