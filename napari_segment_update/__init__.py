from typing import Any
from napari_plugin_engine import napari_hook_implementation

import time
import numpy as np

from napari import Viewer
from napari.layers import Image, Shapes, Labels
from magicgui import magicgui
import napari

from napari.types import LabelsData, ShapesData


def labels_overlap(labels_layer: napari.layers.Labels, 
                   shapes: napari.layers.Shapes, 
                   viewer: napari.Viewer) -> None:
    layerA = labels_layer.data
    layerB = shapes
    if layerB is None:
        viewer.add_shapes(ndim = layerA.ndim)
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
def manually_merge_labels(labels_layer: napari.layers.Labels, 
                          points_layer: napari.layers.Points, 
                          viewer: napari.Viewer):
    
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

def manually_split_labels(labels_layer: Labels, 
                          points_layer: napari.layers.Points, 
                          viewer: napari.Viewer):
    
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

    # origin: https://scikit-image.org/docs/dev/auto_examples/segmentation/plot_watershed.html
    from scipy import ndimage as ndi
    from skimage.segmentation import watershed
    
    mask = np.zeros(labels.shape, dtype=bool)
    for i in points:
        #mask[tuple(points)] = True
        mask[tuple([int(j) for j in i])] = True

    markers, _ = ndi.label(mask)
    new_labels = watershed(binary, markers, mask=binary)
    labels[binary] = new_labels[binary] + labels.max()

    labels_layer.data = labels
    points_layer.data = []

def manually_delete_labels(labels_layer: Labels, 
                           points_layer: napari.layers.Points, 
                           viewer: napari.Viewer):
    
    labels = np.asarray(labels_layer.data)
    if points_layer is None:
        points_layer = viewer.add_points([], ndim = labels.ndim)
        points_layer.mode = 'ADD'
        return
    points = points_layer.data
    print(points)
    print(labels.shape)
    label_ids = [labels.item(tuple([int(j) for j in i])) for i in points]
    print(label_ids)
    for l in label_ids:
            labels[labels == l] = 0

    labels_layer.data = labels
    points_layer.data = []
