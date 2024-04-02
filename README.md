# napari-segment-update

Napari plugin to manually correct segmentation results. 

![A screenshot of the napari-segment-update](https://github.com/aurelien-barbotin/napari-segment-update/blob/main/images/Screenshot-napari-segment-update.png)

This plugin is meant to be used to correct segmentation errors from algorithms like cellpose or omnipose. Such algorithms can make 4 types of operations, corresponding to the 4 types of errors the segmentation algorithm can make:

* Delete labels: Place a series of points above the masks you want to delete, then run delete to remove these maks. In case where the segmentation algorithm invented a mask where there were no cells
* Add labels: Manually draw a shape, then convert it to a mask and add it to the selected labels layers. In case the segmentation algorithm missed a mask
* Split labels: In case of **undersegmentation**, e.g if the algorithm finds one mask where there are two or more cells. Place one point on each cell within the same mask then run.
* Merge labels: In case of **oversegmentation**, e.g if the algorithm finds two or more masks where there is only one cell.

Most of the code comes from this repository: https://www.napari-hub.org/plugins/napari-segment-blobs-and-things-with-membranes

This script mostly adds keyboard shortcuts to speed up the annotation process.

## Usage
Run with 

	python napari_segment_update/script.py

If you are on a ProCeD analysis computer, simply double click on run_napari.bat located in Documents/Python Scripts

Load your masks, either with drag and drop or using File > Open File(s). Once loaded, the masks 

## Install

Simply install napari following official instructions. Last tested with Python 3.9.17 and napari 0.4.18
