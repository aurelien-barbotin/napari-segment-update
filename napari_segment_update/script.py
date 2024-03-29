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
from typing_extensions import Annotated

viewer = napari.Viewer()

@magicgui
def labels_overlap(viewer: napari.Viewer,
                   labels_layer: napari.layers.Labels, 
                   shapes: napari.layers.Shapes):
    """Also called add labels"""
    layerA = labels_layer.data
    layerB = shapes
    if layerB is None:  
        layerB = viewer.add_shapes(ndim = layerA.ndim)
        layerB.mode = "ADD_POLYGON"
        layerB.bind_key('a', lambda x: labels_overlap())
        return
    # useless as shortcuts will work only from label not other layers
    # viewer.layers.selection.select_only(shapes)
    if layerA is not None and layerB is not None:
        bin_A = layerA.copy()
        bin_B = layerB.to_labels()
        out_shape = bin_A.shape
        
        if bin_B.ndim==2:
            bin_B[bin_B!=0]+=layerA.max()
            bin_B = bin_B[:out_shape[0],:out_shape[1]]
            
        elif bin_B.ndim==3:
            bin_B = bin_B[:out_shape[0],:out_shape[1],:out_shape[2]]
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
        bin_B[bin_A[inds_B_mask==out.ndim].reshape(bin_B.shape)!=0] = 0
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
    if viewer.dims.ndim==2:
        for l in label_ids:
            if l != new_label_id:
                labels[labels == l] = new_label_id
    elif viewer.dims.ndim==3:
        current_step = viewer.dims.current_step[0]
        for l in label_ids:
            if l != new_label_id:
                labels[current_step,labels[current_step] == l] = new_label_id
    else:
        return ValueError('Unsupported data format')
    labels_layer.data = labels
    points_layer.data = []

@magicgui(call_button="run", labels_layer={'label':'Label'}, points_layer={'label':'Points'})
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
    if viewer.dims.ndim==2:
        binary = np.zeros(labels.shape, dtype=bool)
        for l in label_ids:
            binary[labels == l] = True
        
        mask = np.zeros(labels.shape, dtype=bool)
        for i in points:
            #mask[tuple(points)] = True
            mask[tuple([int(j) for j in i])] = True
    
        markers, _ = ndi.label(mask)
        new_labels = watershed(binary, markers, mask=binary)
        labels[binary] = new_labels[binary] + labels.max()
        
    elif viewer.dims.ndim==3:
        current_step = viewer.dims.current_step[0]
        binary = np.zeros(labels[current_step].shape, dtype=bool)
        for l in label_ids:
            binary[labels[current_step] == l] = True
        
        mask = np.zeros(labels.shape, dtype=bool)
        for i in points:
            #mask[tuple(points)] = True
            mask[tuple([int(j) for j in i])] = True
        mask=mask[current_step]
        markers, _ = ndi.label(mask)
        new_labels = watershed(binary, markers, mask=binary)
        labels[current_step,binary] = new_labels[binary] + labels.max()
    else:
        raise ValueError('Unsupported data format')

    labels_layer.data = labels
    points_layer.data = []
    return

@magicgui
def manually_delete_labels(viewer: napari.Viewer,
                           points_layer: napari.layers.Points, 
                           labels_layer: napari.layers.Labels,
                           delete_all_atpos: bool,
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
    label_ids = list(filter(lambda x: x!=0,label_ids))
    if viewer.dims.ndim==3:
        current_step = viewer.dims.current_step[0]
        
        if delete_all_atpos:
            for lid in label_ids:
                print("labels id to delete", labels.shape[0], lid)
                msk_todelete = labels[current_step] == lid
                for cs in range(labels.shape[0]):
                    labs = np.unique(labels[cs,msk_todelete])
                    labs = [w for w in labs if w!=0]
                    print("frame  {}, labs: {}".format(cs,labs))
                    print('Labels shape:',labels.shape)
                    for ll in labs:
                        labels[cs,labels[cs] == ll] = 0
        else:
            for l in label_ids:
                    labels[current_step,labels[current_step] == l] = 0
    elif viewer.dims.ndim==2:
        for l in label_ids:
                labels[labels == l] = 0
    else:
        return ValueError('Unsupported dimension')
    labels_layer.data = labels
    points_layer.data = []


viewer.window.add_dock_widget(manually_merge_labels,name='merge labels (R)')
viewer.window.add_dock_widget(labels_overlap,name='add labels (A)')
viewer.window.add_dock_widget(manually_delete_labels,name="delete labels (D)")
viewer.window.add_dock_widget(manually_split_labels,name='split labels (S)')

labelmerger=lambda x: manually_merge_labels()

viewer.bind_key('r', labelmerger)
viewer.bind_key('d', lambda x: manually_delete_labels())
labeloverlapper = lambda x: labels_overlap()
viewer.bind_key('a',labeloverlapper )
viewer.bind_key('s', lambda x: manually_split_labels())
napari.run()
