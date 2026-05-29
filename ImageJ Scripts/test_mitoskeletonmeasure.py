#@ OpService ops
#@ ConvertService convertService
#@ String (label="Threshold Method", required=true, choices={'otsu', 'huang'}) method_threshold
#@ Boolean (label="Save Images?", value=False) save_images
#@ File (label="Input Directory", style="directory") in_dir
#@ File (label="Output Directory", style="directory") out_dir
#@ String (label="Type of image to save as", choices={'jpg', 'tiff', 'png'}) extension

from ij import IJ, Prefs, ImagePlus
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

from sc.fiji import analyzeSkeleton

#  Note; for this plugin we take a binary image from cellprofiler and label it according to the image_object number
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


#def get_single_channel_img():
#	og_imp = IJ.getImage()
#	imp = Duplicator().run(og_imp, 1, 1, 1, 1, 1, 1)
#	return imp

def process_img(imp):
	#Preprocess
	# imp = preprocessing_filters(imp)

	#skeletonize
	IJ.run(imp,"Make Binary","")
	IJ.run(imp, "Skeletonize", "")
	imp = IJ.getImage()
	save_image(imp,"skeleton")
	#IJ.run(imp, "Analyze Skeleton (2D/3D)", "prune=none calculate")
	#IJ.run("Summarize", "");
	imp = run_skel(imp)
	#Save these windows
	rowcolfield= imp.getTitle().split("_")[1]
	IJ.selectWindow("Tagged skeleton")
	tagged_skel = IJ.getImage()
	save_image(tagged_skel,rowcolfield)
	
	IJ.selectWindow("Longest shortest paths")
	shortestpath = IJ.getImage() 
	save_image(shortestpath,rowcolfield)

	return imp
	#run_skel(imp)


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
	for root,dirs,files in os.walk(in_dir):
		for filename in files:
			if ".tiff" in filename:
				img_path = files
				imp = IJ.openImage()
				imp = process_img(imp)
				IJ.run("Close All")
				wm.getWindow("Results").close()
	
if __name__ in ['__builtin__','__main__']:
	run_script()
	
# run AnalyzeSkeleton
# (see https://fiji.sc/AnalyzeSkeleton 
# and https://fiji.sc/javadoc/skeleton_analysis/package-summary.html)
def run_skel(imp):
	skel = AnalyzeSkeleton_()
	skel.setup("",imp)
	skelResult = skel.run(AnalyzeSkeleton_.NONE, False, True, None, True, True)

	# read results
	shortestPaths = skelResult.getShortestPathList().toArray()
	branchLengths = skelResult.getAverageBranchLength()
	branchNumbers = skelResult.getBranches()
	total_length = 0
	for i in range(branchNumbers.length):
		total_length = total_length + (branchNumbers[i] * branchLengths[i])
		
	cumulativeLengthOfShortestPaths = 0
	for i in range(shortestPaths.length):
		cumulativeLengthOfShortestPaths = cumulativeLengthOfShortestPaths + shortestPaths[i]
	
	IJ.log(totalLength)
	IJ.log(cumulativeLengthOfShortestPaths)
	# get the separate skeletons
	'''
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
	'''
	return imp