from napari.utils.notifications import show_info
from napari_plugin_engine import napari_hook_implementation
from napari.layers import Shapes, Image
from napari.types import LabelsData, ShapesData
from functools import partial
import numpy as np

from magicgui import magicgui
from napari import Viewer

def show_hello_message():
    show_info('Hello, world!')


def labels_overlap(labels: LabelsData, shapes: Shapes) -> LabelsData:
    layerA = labels
    layerB = shapes
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

def widget_wrapper():    
    @magicgui(
        layout="vertical",
        create_layer_button  = dict(widget_type='PushButton', text='Choose stack', enabled=True),
        image_layer=Image,)
    def widget(
            image_layer: Image,
            create_layer_button) -> None:
        print("runninf main widget\n\n\n")
        # points_layer = viewer.add_points([])
        # points_layer.mode = 'ADD'
        
    @widget.create_layer_button.changed.connect
    def create_layer():
        print('create layer\n\n')
        
    return widget

@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    return widget_wrapper
