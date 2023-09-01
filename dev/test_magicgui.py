
import napari
from magicgui import magicgui

import numpy as np

viewer = napari.Viewer()

@magicgui(call_button='Make Points', n_points={'maximum': 200})
def make_points(n_points=40) -> napari.types.LayerDataTuple:
  data = 500 * np.random.rand(n_points, 2)
  return (data, {'name': 'My Points'}, 'points')
# make_points['__name__']='make_points'
viewer.window.add_dock_widget(make_points)
# calling this multiple times will just update 'My Points'
make_points()
ptmaker = lambda x: make_points()
viewer.bind_key('r', ptmaker)

napari.run()