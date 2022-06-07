#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 20:56:54 2022

@author: aurelienb
"""

import napari
from magicgui import magicgui
import numpy as np

viewer = napari.Viewer()

@magicgui
def my_widget(viewer: napari.Viewer, labels_layer: napari.layers.Labels,labels_layer2: napari.layers.Labels):
    print(labels_layer.name) if labels_layer else 'None'
"""
@magicgui
def my_widget(viewer: napari.Viewer, labels_layer: napari.layers.Labels):
    print(labels_layer.name) if labels_layer else 'None'
"""
viewer.window.add_dock_widget(my_widget)
# call my_widget when pressing `a`
# of course, you'll need a labels layer for it to work
viewer.bind_key('a', my_widget)
napari.run()