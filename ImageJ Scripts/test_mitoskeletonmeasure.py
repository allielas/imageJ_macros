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
from excel.functions.plugins import ExcelFunctions
import os, csv, re
from collections import OrderedDict
from net.imagej import Dataset

from sc.fiji.analyzeSkeleton import AnalyzeSkeleton_

import sys
sys.path.append("/mnt/bigdisk1/AllieSpangaro/Scripts/imageJ_macros/ImageJ Scripts")
from statistics import median, mean, stdev
import tables

#  Note; for this plugin we take a binary image from cellprofiler and label it according to the image_object number

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

def show_skel_results_table(skelresults): 
	rt = ResultsTable()
	rt.showRowNumbers(True)

	head = ["Skeleton", "# Branches","# Junctions", "# End-point voxels", "# Junction voxels","# Slab voxels","Average Branch Length",  "# Triple points", "# Quadruple points", "Maximum Branch Length", "Longest Shortest Path", "spx", "spy", "spz"]

	for i in range(skelresults.getNumOfTrees()):
		rt.incrementCounter()
	
		rt.addValue(head[ 1], skelresults.getBranches()[i])
		rt.addValue(head[ 2], skelresults.getJunctions()[i])
		rt.addValue(head[ 3], skelresults.getEndPoints()[i])
		rt.addValue(head[ 4], skelresults.getJunctionVoxels()[i])
		rt.addValue(head[ 5], skelresults.getSlabs()[i])
		rt.addValue(head[ 6], skelresults.getAverageBranchLength()[i])
		rt.addValue(head[ 7], skelresults.getTriples()[i])
		rt.addValue(head[ 8], skelresults.getQuadruples()[i])
		rt.addValue(head[ 9], skelresults.getMaximumBranchLength()[i])
		
		#if list is poplated add these to table
		if skelresults.shortestPathList:
			rt.addValue(head[10],skelresults.getShortestPathList().get(i))
			rt.addValue(head[11],skelresults.getSpStartPosition()[i][0])
			rt.addValue(head[12],skelresults.getSpStartPosition()[i][1])
			rt.addValue(head[13],skelresults.getSpStartPosition()[i][2])
	
		if 0 == i % 100: 
			rt.show("Results")
	rt.show("Results")
	active_window_res = wm.getActiveTable()
	active_window_res.removeNotify()
	#IJ.run("Summarize")
	#rt.show("Results")
	return rt

#def get_single_channel_img():
#	og_imp = IJ.getImage()
#	imp = Duplicator().run(og_imp, 1, 1, 1, 1, 1, 1)
#	return imp
# run AnalyzeSkeleton
# (see https://fiji.sc/AnalyzeSkeleton
# and https://fiji.sc/javadoc/skeleton_analysis/package-summary.html)
def analyze_skel(imp, output_parameters, out_path):
	skel = AnalyzeSkeleton_()
	skel.setup("",imp)
	skel_result = skel.run(AnalyzeSkeleton_.NONE, False, True, None, True, True)
	title = imp.getTitle()

	#save skelresult in a seperate dir
	secondary_dir = os.path.join(out_path,"AllSkeletons")
	#print(secondary_dir)
	if not os.path.exists(secondary_dir):
		os.mkdir(secondary_dir)
	skel_csv_filename = os.path.join(secondary_dir,title.split(".")[0]+".csv")
	full_skel_results_table = show_skel_results_table(skel_result)
	full_skel_results_table.saveAs(skel_csv_filename)
#	active_window_skel = wm.getActiveTable()
#	active_window_skel.removeNotify()
#	active_results_skel = active_window_skel.getResultsTable()
#	active_results_skel.updateResults()
#	active_results_skel.save(os.path.join(secondary_dir,title.split(".")[0]+".csv"))
	# read results
	shortest_paths = skel_result.getShortestPathList().toArray()
	avg_branch_lengths = skel_result.getAverageBranchLength()
	branches = list(skel_result.getBranches())
	#max_branch_lengths = skel_result.getMaximumBranchLength()
	#endpoints = skel_result.getEndPoints()
	#junctions = skel_result.getJunctions()

	#calculate totals / max and add to list from the table
	columns = ["# Branches","# Junctions", "# End-point voxels", "# Junction voxels","# Slab voxels","Average Branch Length",  "# Triple points", "# Quadruple points", "Maximum Branch Length", "Longest Shortest Path", "spx", "spy", "spz"]
	totals = []
	maxes = []
	for colname in columns:
		column = full_skel_results_table.getColumn(colname)
		totals.append(sum(column))
		maxes.append(max(column))
	
	totals_dict = dict(zip(columns, totals))
	max_dict = dict(zip(columns, maxes))
	
	#for i in range(len(shortest_paths)):
	#	cumulative_shortestpaths_length = cumulative_shortestpaths_length + shortest_paths[i]
	
	branch_lengths = []
	summed_lengths = []
	graphs = skel_result.getGraph()
	total_length = 0
	num_donuts = 0

	#using classes from https://github.com/StuartLab/MiNA/blob/master/src/scripts/MiNA_Analyze_Morphology.py
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
		total_length += summed_length

	total_length_fromavg = 0
	for i in range(len(branches)):
		#total_length += branch
		total_length_fromavg = total_length + (branches[i] * branch_lengths[i])

#		output_parameters = OrderedDict([("ImageTitle", ""),
#									 ("ImageNumber", ""),
#									 ("Metadata_PlateNumber", ""),
#									 ("Metadata_RowColField", ""),
#									 ("Metadata_ThresholdingOP", float),
#									 #("use ridge detection", ""),
#									 #("mitochondrial footprint", float),
#									 ("BranchLength_Mean", float),
#									 ("BranchLength_Median", float),
#									 ("BranchLength_Stdev", float),
#									 ("SkeletonLength_Mean", float),
#									 ("SkeletonLength_Median", float),
#									 ("SkeletonLength_Stdev", float),
#									 ("SkeletonLength_Max", float),
#									 ("BranchesPerNetwork_Mean", float),
#									 ("BranchesPerNetwork_Median", float),
#									 ("BranchesPerNetwork_Stdev", float),
#									 ("BranchesPerNetwork_Max", float),
#									 ("Total_SkeletonLength", float),
# 									 ("Total_SkeletonLength_FromAvg", float),
#									 ("Total_TriplePoints", float),
#		 							 ("Total_LongestShortestPathLength", float),
#									 ("Total_Donuts", int)])

	output_parameters["ImageTitle"] = title
	output_parameters["ImageNumber"] = get_img_number(title)
	output_parameters["Metadata_PlateNumber"] = get_plate_number(title)
	output_parameters["Metadata_RowColField"] = get_location_code(title)
	output_parameters["Metadata_ThresholdingOP"] = threshold_method
	output_parameters["Total_Donuts"] = num_donuts

	output_parameters["BranchLength_Mean"] = mean(branch_lengths)
	output_parameters["BranchLength_Median"] = median(branch_lengths)
	output_parameters["BranchLength_Stdev"] = stdev(branch_lengths)
	output_parameters["BranchLength_Max"] = max(branch_lengths)

	output_parameters["SkeletonLength_Mean"] = mean(summed_lengths)
	output_parameters["SkeletonLength_Median"] = median(summed_lengths)
	output_parameters["SkeletonLength_Stdev"] = stdev(summed_lengths)
	output_parameters["SkeletonLength_Max"] = max(summed_lengths)

	output_parameters["BranchesPerNetwork_Mean"] = mean(branches)
	output_parameters["BranchesPerNetwork_Median"] = median(branches) #this line is buggy
	output_parameters["BranchesPerNetwork_Stdev"] = stdev(branches)
	output_parameters["BranchesPerNetwork_Max"] = max(branches)

	output_parameters["Total_SkeletonLength"] = total_length
	output_parameters["Total_SkeletonLength_FromAvg"] = total_length_fromavg
	output_parameters["Total_TriplePoints"] = totals_dict.get("# Triple points")
	output_parameters["Total_LongestShortestPathLength"] = totals_dict.get("Longest Shortest Path")
	
	#Todo: add the total and max for TriplePoints, LongestShortestPathLength, avgbranchelngth
	
	
	#print(str(branches) + str(median(branches))
	# Create/append results to a ResultsTable...

	morphology_tbl = tables.SimpleSheet("Mito Morphology")
	morphology_tbl.writeRow(output_parameters)
	morphology_tbl.updateDisplay()
	active_window = wm.getActiveTable()
	active_window.removeNotify()

	#IJ.log(str(total_length))
	#IJ.log(str(cumulative_shortestpaths_length))
	# get the separate skeletons
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

	output_parameters = OrderedDict([("ImageTitle", ""),
									 ("ImageNumber", ""),
									 ("Metadata_PlateNumber", ""),
									 ("Metadata_RowColField", ""),
									 ("Metadata_ThresholdingOP", float),
									 #("use ridge detection", ""),
									 #("mitochondrial footprint", float),
									 ("BranchLength_Mean", float),
									 ("BranchLength_Median", float),
									 ("BranchLength_Stdev", float),
									 ("SkeletonLength_Mean", float),
									 ("SkeletonLength_Median", float),
									 ("SkeletonLength_Stdev", float),
									 ("SkeletonLength_Max", float),
									 ("BranchesPerNetwork_Mean", float),
									 ("BranchesPerNetwork_Median", float),
									 ("BranchesPerNetwork_Stdev", float),
									 ("BranchesPerNetwork_Max", float),
									 ("Total_SkeletonLength", float),
 									 ("Total_SkeletonLength_FromAvg", float),
									 ("Total_TriplePoints", float),
		 							 ("Total_LongestShortestPathLength", float),
									 ("Total_Donuts", int)])
	in_path = in_dir.getAbsolutePath()
	out_path = out_dir.getAbsolutePath()
	new_filename = in_dir.getName()
	csv_filename = new_filename + ".csv"
	csv_path = os.path.join(out_path, csv_filename)
	# open the csv first (if its not there, newly created)

	for root,dirs,files in os.walk(in_path):
		for filename in files:
			if ".tiff" in filename:
				image_path = os.path.join(root,filename)
				imp = IJ.openImage(image_path)
				imp = process_img(imp)
				imp,skelresult = analyze_skel(imp, output_parameters, out_path)

				IJ.run("Close All")
				#
	#now export as csv
	full_csv_filename = os.path.join(out_path,csv_filename)
	skelresult.rt.save(full_csv_filename)
	print("Saved at " + os.path.join(out_path,csv_filename))
	#f = open(csv_path, 'wb')#, newline='') #"wb"
	#writer = csv.writer(f)
	#add_results_to_csv(skelresult, writer, out_path)
	#IJ.selectWindow("Mito Morphology")
	#IJ.saveAs("Results", os.path.join(out_path,csv_filename))

	# cleanup
	IJ.run("Clear Results")
	wm.getWindow("Mito Morphology").close()
	wm.getWindow("Results").close()
if __name__ in ['__builtin__','__main__']:
	run_script()
