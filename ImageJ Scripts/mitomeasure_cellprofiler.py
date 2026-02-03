#@String directory
#@ OpService ops

from ij import IJ, Prefs
from ij import WindowManager as wm
from ij.gui import WaitForUserDialog, Roi, ShapeRoi, Toolbar
from ij.plugin import Duplicator
from ij.measure import ResultsTable
from ij.plugin.frame import RoiManager 

import os


#from ij.skeleton_analysis import AnalyzeSkeleton_,Graph,Edge,Vertex
# from the mina plugin
def ridge_detect(imp, rd_max, rd_min, rd_width, rd_length):
    title = imp.getTitle()
    IJ.run(imp, "8-bit", "");
    IJ.run(imp, "Ridge Detection", "line_width=%s high_contrast=%s low_contrast=%s make_binary method_for_overlap_resolution=NONE minimum_line_length=%s maximum=0" % (rd_width, rd_max, rd_min, rd_length))
    IJ.run(imp, "Remove Overlay", "")
    skel = wm.getImage(title + " Detected segments")
    IJ.run(skel, "Skeletonize (2D/3D)", "")
    skel.hide()
    return(skel)
    

def preprocessing_filters(imp, median_radius=2, unsharp_radius=1,unsharp_weight=0.60,clahe_block=127,clahe_bins=256,clahe_slope=3,clahe_mask="*None*"):
	IJ.run(imp, "Median...", "radius=%s" % (median_radius))
	IJ.run(imp, "Unsharp Mask...", "radius=%s mask=%s" % (unsharp_radius, unsharp_weight))
	        
	IJ.run(imp, "Enhance Local Contrast (CLAHE)", "blocksize=%s histogram=%s maximum=%s mask=%s fast_(less_accurate)" % (clahe_block, clahe_bins, clahe_slope, clahe_mask))
	#IJ.run(imp, "Enhance Local Contrast (CLAHE)", "blocksize=127 histogram=256 maximum=3 mask=*None* fast_(less_accurate)")
	return imp

def resize_img_by_roi_coords(rm, imp):
	rois = rm.getRoisAsArray() # this is a list of rois (only 1 as it got cleared
	lastroi = rois[-1]
	bounds = lastroi.getBounds()
	roiarea = bounds.width * bounds.height
	print("Area:",roiarea, " Bounds:", bounds)
	#IJ.run(imp, "Clear Outside", "");
	imp = imp.resize(bounds.width, bounds.height, "bilinear")
	return imp

def get_single_channel_img():
	og_imp = IJ.getImage()
	imp = Duplicator().run(og_imp, 1, 1, 1, 1, 1, 1)
	print(imp.getTitle())	
	return imp

def threshold(imp, method_threshold="Otsu",relative_threshold="1"):
	from net.imglib2.type.numeric.integer import UnsignedByteType
	# Get the histogram
	histo = ops.run("image.histogram", imp)
	# Get the threshold
	threshold_value = ops.run("threshold.%s" % method_threshold, histo)
	# Modulate 'threshold_value' by 'relative_threshold'
	threshold_value = int(round(threshold_value.get() * relative_threshold))
	# We should not have to do that...
	threshold_value = UnsignedByteType(threshold_value)
	# Apply the threshold
	thresholded = ops.run("threshold.apply", data, threshold_value)
	return thresholded

def process_img(imp):
	#Preprocess
	imp = preprocessing_filters(imp)
	IJ.saveAs(imp,'tiff',os.path.join(directory,'_preprocessed.tiff'))
	#threshold and skeletonize

	imp.setAutoThreshold("Otsu dark 16-bit no-reset")
	Prefs.blackBackground = True
	IJ.run(imp,"Make Binary","") #IJ.run(imp, "Convert to Mask", "")
	IJ.run(imp, "Open", "");
	im2 = IJ.getImage()
	IJ.saveAs(im2,'tiff',os.path.join(directory,'_threshmito.tiff'))
	
	IJ.run(imp, "Skeletonize", "")
	im3 = IJ.getImage()
	IJ.saveAs(im3,'tiff',os.path.join(directory,'_skelmito.tiff'))
	IJ.run(imp, "Analyze Skeleton (2D/3D)", "") #prune=[shortest branch] prune_0 calculate
	
	return imp
	#run_skel(imp)

# open image
#if using CP, assumes you are giving it a single-channel image
def open_img(imp):
	#IJ.run(imp,"Gaussian Blur...","sigma=2")
	imp = IJ.open(os.path.join(directory, 'mito.tiff'))
	return imp

if __name__ in ['__builtin__','__main__']:
	imp = open_img
	processed_img = process_img(imp)


