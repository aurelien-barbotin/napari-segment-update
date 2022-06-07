#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 10:57:05 2022

@author: aurelienb
"""

import napari

import pandas as pd
from napari.layers import Shapes
import tifffile
import numpy as np

path = "/home/aurelienb/Documents/Projects/2022_02_Louise/test_shapes.csv"
aa = pd.read_csv("/home/aurelienb/Documents/Projects/2022_02_Louise/test_shapes.csv")

layerA = tifffile.imread("/home/aurelienb/Documents/Projects/2022_02_Louise/resized_testim_labels.tif")
layerB = napari.utils.io.csv_to_layer_data(path)

layerB = Shapes( data=layerB[0], shape_type=layerB[1]['shape_type'])

if layerA is not None and layerB is not None:
    bin_A = layerA.copy()
    bin_B = layerB.to_labels()
    out_shape = ( [max(bin_A.shape[j], bin_B.shape[j]) 
                  for j in range(layerA.ndim)] )
    bin_B[bin_B!=0]+=layerA.max()
    out = np.zeros(out_shape, dtype = int)
    
    indsA =  np.indices(out.shape) 
    print(out.shape, indsA.shape)
    inds_A_mask = np.array([indsA[j]< bin_A.shape[j] 
                             for j in range(out.ndim)]).astype(int)
    print(inds_A_mask.shape)
    inds_A_mask = inds_A_mask.sum(axis=0)
    out[inds_A_mask==out.ndim]+=bin_A.reshape(-1)
    
    inds_B_mask = np.array([indsA[j]< bin_B.shape[j] 
                             for j in range(out.ndim)]).astype(int).sum(axis=0)
    
    out[inds_B_mask==out.ndim]+=bin_B.reshape(-1)
    labels = out