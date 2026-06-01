#@ OpService ops
#@ LogService log
#@ ConvertService convertService
#@ String (label="Threshold Method", required=true, choices={'otsu', 'huang'}) threshold_method
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

import os, csv, re
from collections import OrderedDict
from net.imagej import Dataset

from sc.fiji.analyzeSkeleton import AnalyzeSkeleton_

import sys
sys.path.append("/mnt/bigdisk1/AllieSpangaro/Scripts/imageJ_macros/ImageJ Scripts")
from statistics import median, mean, stdev
import tables

#  Note; for this plugin we take a binary image from cellprofiler and label it according to the image_object number
#from ij.skeleton_analysis import AnalyzeSkeleton_,Graph,Edge,Vertex
# from the mina plugin
def ridge_detect(imp, rd_max, rd_min, rd_width, rd_length):
	title = imp.getTitle()
	IJ.run(imp, "8-bit", "");
	#IJ.run(imp, "Ridge Detection", "line_width=%s high_contrast=%s low_contrast=%s make_binary method_for_overlap_resolution=NONE minimum_line_length=%s maximum=0" % (rd_width, rd_max, rd_min, rd_length))
	IJ.run(imp, "Remove Overlay", "")
	skel = wm.getImage(title + " Detected segments")
	IJ.run(skel, "Skeletonize (2D/3D)", "")
	skel.hide()
	return(skel)

def threshold(imp):
	# Get the histogram
	print(imp)
	data = convertService.convert(imp, Dataset)
	thresholded = ops.run("threshold.%s" % threshold_method, data)
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

def get_location_code(file_name):
    match = re.search(r"(r\d{2}c\d{2}f\d{2})", file_name)
    if match:
        # print(match.group(0))  # Print the full match for debugging
        return match.group(1)
    else:
        return None

def get_plate_number(file_name):
    match = re.search(r"rep(\d{1,2})", file_name)
    if match:
        return match.group(1)
    else:
        return None
        
def get_img_number(file_name):
	#image number at end of filename
	file_name_noext = file_name.split(".")[0]
	match = re.search(r"_(\d{1,2})$", file_name_noext)
	if match:
	    return match.group(1) # get last match
	else:
	    return None

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
# run AnalyzeSkeleton
# (see https://fiji.sc/AnalyzeSkeleton 
# and https://fiji.sc/javadoc/skeleton_analysis/package-summary.html)
def analyze_skel(imp, output_parameters):
	skel = AnalyzeSkeleton_()
	skel.setup("",imp)
	skel_result = skel.run(AnalyzeSkeleton_.NONE, False, True, None, True, True)

	# read results
	shortest_paths = skel_result.getShortestPathList().toArray()
	branch_lengths = skel_result.getAverageBranchLength()
	#max_branch_lengths = skel_result.getMaximumBranchLength() 
	branch_numbers = skel_result.getBranches()
	#endpoints = skel_result.getEndPoints()
	#junctions = skel_result.getJunctions()
	triples = skel_result.getTriples()
	#calculate totals
	total_length = 0
	for i in range(len(branch_numbers)):
		total_length = total_length + (branch_numbers[i] * branch_lengths[i])
		
	cumulative_shortestpaths_length = 0
	for i in range(len(shortest_paths)):
		cumulative_shortestpaths_length = cumulative_shortestpaths_length + shortest_paths[i]
		
	total_triplepoints = 0
	for i in range(len(triples)):
		total_triplepoints = total_triplepoints + triples[i]
	
	branch_lengths = []
	summed_lengths = []
	graphs = skel_result.getGraph()
	
	#using classes from https://github.com/StuartLab/MiNA/blob/master/src/scripts/MiNA_Analyze_Morphology.py
	num_donuts = 0
	for graph in graphs:
		summed_length = 0.0
		edges = graph.getEdges()
		vertices = {}
		for edge in edges:
			length = edge.getLength()
			branch_lengths.append(length)
			summed_length += length

			# keep track of the number of times a vertex appears in edges in a given graph
			for vertex in [edge.getV1(), edge.getV2()]:
				if vertex in vertices:
					vertices[vertex] += 1
				else:
					vertices[vertex] = 1
		is_donut = True
		# donut_arms = 0
		for k in vertices:
			# if a vertex appeared less than twice
			if vertices[k] <= 1:
				# donut_arms += 1
				# if donut_arms > 1:
				is_donut = False
				break

		if is_donut and len(edges) >= 1:
			num_donuts += 1

		summed_lengths.append(summed_length)
	
	title = imp.getTitle()
	output_parameters["image title"] = title
	output_parameters["ImageNumber"] = get_img_number(title)
	output_parameters["PlateNumber"] = get_plate_number(title)
	output_parameters["Metadata_WellColField"] = get_location_code(title)
	output_parameters["thresholding op"] = threshold_method
	output_parameters["donuts"] = num_donuts
	
	output_parameters["branch length mean"] = mean(branch_lengths)
	output_parameters["branch length median"] = median(branch_lengths)
	output_parameters["branch length stdev"] = stdev(branch_lengths)
	
	output_parameters["summed branch lengths mean"] = mean(summed_lengths)
	output_parameters["summed branch lengths median"] = median(summed_lengths)
	output_parameters["summed branch lengths stdev"] = stdev(summed_lengths)
	
	branches = list(skel_result.getBranches())
	output_parameters["network branches mean"] = mean(branches)
	output_parameters["network branches median"] = median(branches) #this line is buggy
	output_parameters["network branches stdev"] = stdev(branches)
	
	output_parameters["total skeleton length"] = total_length
	output_parameters["total triple points"] = total_triplepoints
	output_parameters["cumulative longest shortest path length"] = cumulative_shortestpaths_length
	#print(str(branches) + str(median(branches))
	# Create/append results to a ResultsTable...
	
	morphology_tbl = tables.SimpleSheet("Mito Morphology")
	activewindow = wm.getActiveTable()
	activewindow.removeNotify() 
	morphology_tbl.writeRow(output_parameters)
	morphology_tbl.updateDisplay()
	
	#IJ.log(str(total_length))
	#IJ.log(str(cumulative_shortestpaths_length))
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
	return imp, morphology_tbl

def process_img(imp):
	#Preprocess
	# imp = preprocessing_filters(imp)

	#skeletonize
	IJ.run(imp,"Make Binary","")
	IJ.run(imp, "Skeletonize (2D/3D)", "")
	#imp = IJ.getImage()
	save_image(imp,"skeleton")
	#IJ.run(imp, "Analyze Skeleton (2D/3D)", "prune=none calculate")
	#IJ.run("Summarize", "");
	#Save these windows
	#IJ.selectWindow("Tagged skeleton")
	#tagged_skel = IJ.getImage()
	#save_image(tagged_skel,rowcolfield)
	
	#IJ.selectWindow("Longest shortest paths")
	#shortestpath = IJ.getImage() 
	#save_image(shortestpath,rowcolfield)

	return imp
	#run_skel(imp)

def save_image(imp, prefix="", extension=extension, force_3char=False):
	imp2 = imp.clone()
	if save_images:
		title = imp2.getTitle()
		if "DUP_" in title:
			title = title.split("_")[1]
		out_path = out_dir.getAbsolutePath()
		if not os.path.exists(out_path):
			os.makedirs(out_dir)
		  # if you need the 3 char tif extension
		if extension == "tiff" and force_3char:
			extension = "tif"
		
		#make the title attach to the required extension
		if title.endswith(extension):
			filename = title.split(".")[0]
		else:
			filename = title
		title_string = (prefix + '_' + filename + '.' + extension)
		
		print(title_string)
		IJ.saveAs(imp2,extension,os.path.join(out_path,title_string))
		imp2.close()
		return True
	else:
		return False

def add_results_to_csv(skelresults, writer, out_path):
	# make the headings and then add the column values based on the column names
	headings = skelresults.getRow(0).keys()
	headings_list = list(headings)
	print(headings_list)
	writer.writerow(headings_list)
	
	for i in range(skelresults.rt.getCounter()):
		row_values = skelresults.getRow(i).values() #this returns a dict but we only care about the numbers
		row_list = list(row_values)
		print(row_list)
		writer.writerow(row_list)
	return True

def run_script():
	
	output_parameters = OrderedDict([("image title", ""),
									 ("ImageNumber", ""),
									 ("PlateNumber", ""),
									 ("Metadata_WellColField", ""),
									 ("thresholding op", float),
									 #("use ridge detection", ""),
									 #("mitochondrial footprint", float),
									 ("branch length mean", float),
									 ("branch length median", float),
									 ("branch length stdev", float),
									 ("summed branch lengths mean", float),
									 ("summed branch lengths median", float),
									 ("summed branch lengths stdev", float),
									 ("network branches mean", float),
									 ("network branches median", float),
									 ("network branches stdev", float),
									 ("total skeleton length", float),
									 ("total triple points", float),
		 							 ("cumulative longest shortest path length", float),
									 ("donuts", int)])					 
	in_path = in_dir.getAbsolutePath()
	out_path = out_dir.getAbsolutePath()
	csv_filename = "testdata2.csv"
	csv_path = os.path.join(out_path, csv_filename)
	# open the csv first (if its not there, newly created)

	for root,dirs,files in os.walk(in_path):
		for filename in files:
			if ".tiff" in filename:
				image_path = os.path.join(root,filename)
				imp = IJ.openImage(image_path)
				imp = process_img(imp)
				imp,skelresult = analyze_skel(imp, output_parameters)
				
				IJ.run("Close All")
				#
	#now export as csv
	#f = open(csv_path, 'wb')#, newline='') #"wb"
	#writer = csv.writer(f)
	#add_results_to_csv(skelresult, writer, out_path)

	IJ.saveAs("Results", os.path.join(out_path,csv_filename))
	print("Saved at " + os.path.join(out_path,csv_filename))

	#wm.getWindow("Mito Morphology").close()
if __name__ in ['__builtin__','__main__']:
	run_script()
	
