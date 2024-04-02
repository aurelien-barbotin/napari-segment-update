# napari-segment-update

Napari plugin to manually correct segmentation results. This plugin is meant to be used to correct segmentation errors from algorithms like cellpose or omnipose. Such algorithms can make 4 types of errors, therefore 4 operations are allowed by this plugin:

* Oversegmentation: 

Most of the code comes from here: https://www.napari-hub.org/plugins/napari-segment-blobs-and-things-with-membranes

This script mostly adds keyboard shortcuts to speed up the annotation process.

## Usage
Run with 

	python napari_segment_update/script.py
	
## Install

Simply install napari following official instructions. Last tested with Python 3.9.17 and napari 0.4.18
