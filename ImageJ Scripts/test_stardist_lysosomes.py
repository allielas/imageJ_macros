#@String directory

from ij import IJ, ImagePlus
import os
from ij import WindowManager
from ij.plugin.frame import RoiManager
rm = RoiManager.getInstance()
if not rm:
	rm = RoiManager()

probThresh = "0.3"
overlapLevel = "0.4"
title = "dummy.tiff"
im = IJ.open(os.path.join(directory, title))
#run("Morphological Filters", "operation=[White Top Hat] element=Disk radius=15");
#IJ.saveAs(im2,'tiff',os.path.join(directory,'outlines.tiff'))
IJ.run("StarDist 2D", "command=de.csbdresden.stardist.StarDist2D args=['input':'"+title+"', 'modelChoice':'Versatile (fluorescent nuclei)', 'normalizeInput':'true', 'percentileBottom':'1.0', 'percentileTop':'99.8', 'probThresh':'0.30000000000000004', 'nmsThresh':'0.4', 'outputType':'ROI Manager', 'nTiles':'1', 'excludeBoundary':'2', 'roiPosition':'Automatic', 'verbose':'true', 'showCsbdeepProgress':'false', 'showProbAndDist':'false'] process=false")

totalRois = rm.getCount()
if totalRois > 0:
	IJ.run("ROIs to Label image")
	im2 = IJ.getImage()
	IJ.saveAs(im2,'tiff',os.path.join(directory,'outlines.tiff'))
	IJ.exit()
else:
	IJ.exit("No ROIs in image")
