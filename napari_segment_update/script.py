#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 20:12:27 2022

@author: aurelienb
"""

import napari
from magicgui import magicgui

from scipy import ndimage as ndi
from skimage.segmentation import watershed
import numpy as np

viewer = napari.Viewer()

@magicgui
def labels_overlap(viewer: napari.Viewer,
                   labels_layer: napari.layers.Labels, 
                   shapes: napari.layers.Shapes):
    layerA = labels_layer.data
    layerB = shapes
    if layerB is None:
        layerB = viewer.add_shapes(ndim = layerA.ndim)
        layerB.mode = "ADD_POLYGON"
        layerB.bind_key('a', labels_overlap)
        return
    if layerA is not None and layerB is not None:
        bin_A = layerA.copy()
        bin_B = layerB.to_labels()
        out_shape = ([max(bin_A.shape[j], bin_B.shape[j]) 
                      for j in range(layerA.ndim)] )
        if bin_B.ndim==2:
            bin_B[bin_B!=0]+=layerA.max()
        elif bin_B.ndim==3:
            for j in range(bin_B.shape[0]):
                bin_B[j,bin_B[j]!=0]+=layerA[j].max()
        # merge two layers together
        out = np.zeros(out_shape, dtype = int)
        indsA =  np.indices(out.shape)         
        inds_A_mask = np.array([indsA[j]< bin_A.shape[j] 
                                 for j in range(out.ndim)]).astype(int)
        inds_A_mask = inds_A_mask.sum(axis=0)
        out[inds_A_mask==out.ndim]+=bin_A.reshape(-1)
        
        inds_B_mask = np.array([indsA[j]< bin_B.shape[j] 
                                 for j in range(out.ndim)]).astype(int).sum(axis=0)
        
        out[inds_B_mask==out.ndim]+=bin_B.reshape(-1)
        labels_layer.data = out
        shapes.data = []

# Stolen here 
# https://www.napari-hub.org/plugins/napari-segment-blobs-and-things-with-membranes
@magicgui
def manually_merge_labels(
                        viewer: napari.Viewer,
                        labels_layer: napari.layers.Labels, 
                        points_layer: napari.layers.Points ):
    
    labels = np.asarray(labels_layer.data)
    if points_layer is None:
        points_layer = viewer.add_points([], ndim = labels.ndim)
        points_layer.mode = 'ADD'
        return
    points = points_layer.data

    label_ids = [labels.item(tuple([int(j) for j in i])) for i in points]

    # replace labels with minimum of the selected labels
    new_label_id = min(label_ids)
    for l in label_ids:
        if l != new_label_id:
            labels[labels == l] = new_label_id

    labels_layer.data = labels
    points_layer.data = []
    
@magicgui
def manually_split_labels(viewer: napari.Viewer,
                          labels_layer: napari.layers.Labels, 
                          points_layer: napari.layers.Points):
    
    labels = np.asarray(labels_layer.data)
    if points_layer is None:
        points_layer = viewer.add_points([], ndim = labels.ndim)
        points_layer.mode = 'ADD'
        return

    points = points_layer.data

    label_ids = [labels.item(tuple([int(j) for j in i])) for i in points]

    # make a binary image first
    binary = np.zeros(labels.shape, dtype=bool)
    new_label_id = min(label_ids)
    for l in label_ids:
        binary[labels == l] = True
    
    mask = np.zeros(labels.shape, dtype=bool)
    for i in points:
        #mask[tuple(points)] = True
        mask[tuple([int(j) for j in i])] = True

    markers, _ = ndi.label(mask)
    new_labels = watershed(binary, markers, mask=binary)
    labels[binary] = new_labels[binary] + labels.max()

    labels_layer.data = labels
    points_layer.data = []
    
@magicgui
def manually_delete_labels(viewer: napari.Viewer,
                           points_layer: napari.layers.Points, 
                           labels_layer: napari.layers.Labels
                           ):
    if labels_layer is None:
        print('labels is None')
        return
    
    labels = np.asarray(labels_layer.data)
    if points_layer is None:
        points_layer = viewer.add_points([], ndim = labels.ndim)
        points_layer.mode = 'ADD'
        return
    points = points_layer.data
    label_ids = [labels.item(tuple([int(j) for j in i])) for i in points]
    for l in label_ids:
            labels[labels == l] = 0

    labels_layer.data = labels
    points_layer.data = []

viewer.window.add_dock_widget(manually_merge_labels,name='merge labels (R)')
viewer.window.add_dock_widget(manually_split_labels,name='split labels (S)')
viewer.window.add_dock_widget(labels_overlap,name='add labels (A)')
viewer.window.add_dock_widget(manually_delete_labels,name="delete labels (D)")
# call my_widget when pressing `a`
# of course, you'll need a labels layer for it to work
viewer.bind_key('r', manually_merge_labels)
viewer.bind_key('d', manually_delete_labels)
viewer.bind_key('s', manually_split_labels)
viewer.bind_key('a', labels_overlap)
napari.run()