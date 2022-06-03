from typing import Any
from napari_plugin_engine import napari_hook_implementation

import time
import numpy as np

from napari import Viewer
from napari.layers import Image, Shapes
from magicgui import magicgui
import napari

from napari.types import LabelsData, ShapesData

def labels_overlap(labels: LabelsData, shapes: Shapes, viewer: napari.Viewer) -> LabelsData:
    layerA = labels
    layerB = shapes
    if layerB is None:
        viewer.add_shapes(ndim = layerA.ndim)
    if layerA is not None and layerB is not None:
        bin_A = layerA.copy()
        bin_B = layerB.to_labels()
        out_shape = (max(bin_A.shape[0], bin_B.shape[0]),
                     max(bin_A.shape[1], bin_B.shape[1]) )
        print(out_shape)
        bin_B[bin_B!=0]+=layerA.max()
        out = np.zeros(out_shape)
        out[:bin_A.shape[0],:bin_A.shape[1]]+=bin_A
        out[:bin_B.shape[0],:bin_B.shape[1]]+=bin_B
        return out.astype(int)

# Stolen here 
# https://www.napari-hub.org/plugins/napari-segment-blobs-and-things-with-membranes
def manually_merge_labels(labels_layer: napari.layers.Labels, points_layer: napari.layers.Points, viewer: napari.Viewer):
    if points_layer is None:
        points_layer = viewer.add_points([])
        points_layer.mode = 'ADD'
        return
    labels = np.asarray(labels_layer.data)
    points = points_layer.data

    label_ids = [labels.item(tuple([int(j) for j in i])) for i in points]

    # replace labels with minimum of the selected labels
    new_label_id = min(label_ids)
    for l in label_ids:
        if l != new_label_id:
            labels[labels == l] = new_label_id

    labels_layer.data = labels
    points_layer.data = []

def manually_split_labels(labels_layer: napari.layers.Labels, points_layer: napari.layers.Points, viewer: napari.Viewer):
    if points_layer is None:
        points_layer = viewer.add_points([])
        points_layer.mode = 'ADD'
        return

    labels = np.asarray(labels_layer.data)
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
    #from skimage.feature import peak_local_max

    #distance = ndi.distance_transform_edt(binary)
    #coords = peak_local_max(distance, footprint=np.ones((3, 3)), labels=binary)
    mask = np.zeros(labels.shape, dtype=bool)
    for i in points:
        #mask[tuple(points)] = True
        mask[tuple([int(j) for j in i])] = True

    markers, _ = ndi.label(mask)
    new_labels = watershed(binary, markers, mask=binary)
    labels[binary] = new_labels[binary] + labels.max()

    labels_layer.data = labels
    points_layer.data = []
