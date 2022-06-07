#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 13:49:55 2022

@author: aurelienb
"""

import napari

import pandas as pd
from napari.layers import Shapes, Points, Labels
import tifffile
import numpy as np

path = "/home/aurelienb/Documents/Projects/2022_02_Louise/test_shapes.csv"
aa = pd.read_csv("/home/aurelienb/Documents/Projects/2022_02_Louise/test_shapes.csv")

layerA = tifffile.imread("/home/aurelienb/Documents/Projects/2022_02_Louise/resized_testim_labels.tif")
layerB = napari.utils.io.csv_to_layer_data(path)

points_layer = Points(data = np.array([[250.28360214, 389.99365285],
       [232.25059869, 440.22844817]]))

labels = layerA
points = points_layer.data

label_ids = [labels.item(tuple([int(j) for j in i])) for i in points]
print(label_ids)
for l in label_ids:
        labels[labels == l] = 0
