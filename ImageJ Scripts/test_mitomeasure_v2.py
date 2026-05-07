#@ OpService ops
#@ ConvertService convertService
#@ String (label="Threshold Method", required=true, choices={'otsu', 'huang'}) method_threshold
#@ Boolean (label="Save Images?", value=False) save_images
#@ File (label="Output Directory", style="directory") out_dir
#@ String (label="Type of image to save as", choices={'jpg', 'tiff', 'png'}) extension

from ij import IJ, Prefs
from ij import WindowManager as wm
from ij.gui import WaitForUserDialog, Roi, ShapeRoi, Toolbar
from ij.plugin import Duplicator
from ij.measure import ResultsTable
from ij.plugin.frame import RoiManager 

from net.imagej.axis import Axes
from net.imglib2.util import Intervals
import os

from net.imglib2.type.numeric.integer import UnsignedByteType
from net.imagej import Dataset
from ij import ImagePlus

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

def threshold(imp):
	# Get the histogram
	print(imp)
	data = convertService.convert(imp, Dataset)
	thresholded = ops.run("threshold.%s" % method_threshold, data)
	imp = convertService.convert(thresholded, ImagePlus)
	IJ.run(imp,"Make Binary","")
	imp = IJ.getImage()
	save_image(imp,"thresh")
	return imp
	
def classic_threshold(imp):
	IJ.resetThreshold(imp);
	#imp.setDisplayRange(219, 7982);
	imp.updateAndDraw()
	imp.setAutoThreshold("Otsu dark 16-bit no-reset")
	Prefs.blackBackground = True
	IJ.run(imp,"Make Binary","") #IJ.run(imp, "Convert to Mask", "")
	return imp

def preprocessing_filters(imp, median_radius=2, unsharp_radius=1,unsharp_weight=0.60,clahe_block=127,clahe_bins=256,clahe_slope=3,clahe_mask="*None*"):
	IJ.run(imp, "Median...", "radius=%s" % (median_radius))
	IJ.run(imp, "Unsharp Mask...", "radius=%s mask=%s" % (unsharp_radius, unsharp_weight))    
	IJ.run(imp, "Enhance Local Contrast (CLAHE)", "blocksize=%s histogram=%s maximum=%s mask=%s fast_(less_accurate)" % (clahe_block, clahe_bins, clahe_slope, clahe_mask))
	#IJ.run(imp, "Enhance Local Contrast (CLAHE)", "blocksize=127 histogram=256 maximum=3 mask=*None* fast_(less_accurate)")
	if save_images:
		IJ.run(imp, "Enhance Contrast", "saturated=0.35");
		save_image(imp,"preprocessed")
	return imp

def resize_img_by_roi_coords(rm, imp):
	rois = rm.getRoisAsArray() # this is a list of rois (only 1 as it got cleared
	lastroi = rois[-1]
	imp.setRoi(lastroi)
	bounds = lastroi.getBounds()
	roiarea = bounds.width * bounds.height
	print("Area:",roiarea, " Bounds:", bounds)
	#IJ.run(imp, "Clear Outside", "");
	IJ.setBackgroundColor(0, 0, 0);
	IJ.run(imp, "Clear Outside", "");
	imp.resize(bounds.width, bounds.height, "bilinear")
	return imp,roiarea

def get_single_channel_img():
	og_imp = IJ.getImage()
	imp = Duplicator().run(og_imp, 1, 1, 1, 1, 1, 1)
	return imp

def process_img(imp):
	#Preprocess
	imp = preprocessing_filters(imp)
	imp.show()

	#Prompt user to make an ROI selection
	rm = RoiManager.getInstance()
	if not rm:
		rm = RoiManager()
	#IJ.setTool("polygon");
	IJ.setTool(Toolbar.POLYGON)
	WaitForUserDialog("Select the area,then click OK.").show()
	roi1 = imp.getRoi()
	imp.setRoi(roi1)
	rm.addRoi(roi1)
	imp, roiarea = resize_img_by_roi_coords(rm, imp)

	#threshold and skeletonize
	imp = threshold(imp)
	
	IJ.run(imp, "Skeletonize", "")
	imp = IJ.getImage()
	save_image(imp,"skeleton")
	IJ.run(imp, "Analyze Skeleton (2D/3D)", "prune=none calculate")
	IJ.run("Summarize", "");
	
	#Save these windows
	rowcolfield= imp.getTitle().split("_")[1]
	IJ.selectWindow("Tagged skeleton")
	tagged_skel = IJ.getImage()
	save_image(tagged_skel,rowcolfield)
	
	IJ.selectWindow("Longest shortest paths")
	shortestpath = IJ.getImage() 
	save_image(shortestpath,rowcolfield)
	
	WaitForUserDialog("ROI area =%s Click Ok to close windows." % (roiarea)).show()
	return imp
	#run_skel(imp)

# open image, blur, make b/w, skeletonize
def open_img(imp):
	#IJ.run(imp,"Gaussian Blur...","sigma=2")
	imp = IJ.openImage("/path/to/image.tif")
	return imp

def save_image(imp, prefix="", extension=extension):
	imp2 = imp.clone()
	if save_images:
		title = imp2.getTitle()
		if "DUP_" in title:
			title = title.split("_")[1]
		out_path = out_dir.getAbsolutePath()
  		if not os.path.exists(out_path):
  			os.makedirs(out_dir)
		if extension == "tiff":
			save_ext = "tif"
			extension = "Tiff"
			title_string = (prefix + '_' + title + '.' + save_ext)
		else:
			title_string = (prefix + '_' + title + '.' + extension)
		print(title_string)
		IJ.saveAs(imp2,extension,os.path.join(out_path,title_string))
		imp2.close()
		return True
	else:
		return False

def run_script():
	imp = get_single_channel_img()
	imp = process_img(imp)
	IJ.run("Close All")
	wm.getWindow("Results").close()
	
if __name__ in ['__builtin__','__main__']:
	run_script()

'''
# run AnalyzeSkeleton
# (see https://fiji.sc/AnalyzeSkeleton 
# and https://fiji.sc/javadoc/skeleton_analysis/package-summary.html)
def run_skel(imp):
	skel = AnalyzeSkeleton_()
	skel.setup("",imp)
	skelResult = skel.run(skel.NONE, False, True, None, True, True)

	# get the separate skeletons
	graph = skelResult.getGraph()
	print len(graph)
	print skelResult.getNumOfTrees()

	def getGraphLength(graph):
	    length = 0
	    for g in graph.getEdges():
	    	length = length + g.getLength()
	    return length
	# find the longest graph
	graph = sorted(graph, key=lambda g: getGraphLength(g), reverse=True)
	longestGraph = graph[0]
	
	# find the longest edge
	edges = longestGraph.getEdges()
	edges = sorted(edges, key=lambda edge: edge.getLength(), reverse=True)
	longestEdge = edges[0]
	
	print(longestGraph, longestEdge)
	return imp
'''