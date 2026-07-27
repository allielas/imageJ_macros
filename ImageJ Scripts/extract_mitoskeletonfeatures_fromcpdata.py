# @ OpService ops
# @ LogService log
# @ ConvertService convertService
# @ String (label="Threshold Method", required=true, choices={'otsu', 'huang'}) threshold_method
# @ Boolean (label="Save Images?", value=False) save_images
# @ Boolean (label="Run through multiple batches in a parent folder?", value=False) batch_folder
# @ File (label="Input Directory", style="directory") in_dir
# @ File (label="Output Directory", style="directory") out_dir
# @ String (label="Type of image to save as", choices={'jpg', 'tiff', 'png'}) extension
# @ File (label="Repo Directory", style="directory") repo_dir

from ij import IJ, Prefs, ImagePlus
from ij import WindowManager as wm
from ij.plugin import Duplicator
from ij.measure import ResultsTable, Measurements
from excel.functions.plugins import ExcelFunctions
import os, csv, re, sys
from collections import OrderedDict
from net.imagej import Dataset
from sc.fiji.analyzeSkeleton import AnalyzeSkeleton_

# from net.imglib2.img.display.imagej import ImageJFunctions
# import the MinA functions for analyzing the skeletons, we will use some of the code from MiNA_Analyze_Morphology.py to do this
repo_path = repo_dir.getAbsolutePath()
sys.path.append(os.path.join(repo_path, "ImageJ Scripts"))
from statistics import median, mean, stdev
import tables

#  Note; for this plugin we take a binary image from cellprofiler and label it according to the image_object number

def get_location_code(file_name):
	match = re.search(r"(r\d{2}c\d{2}f\d{2})", file_name)
	if match:
		# print(match.group(0))  # Print the full match for debugging
		return match.group(1)
	else:
		return None


def get_plate_number(file_name,image_path):
	match = re.search(r"rep(\d{1,2})", file_name)
	if match:
		return match.group(1)
	else:
		match = re.search(r"rep(\d{1,2})", image_path)
		if match:
			return match.group(1)
		else:
			return None


def get_object_number(file_name):
	# image number at end of filename
	file_name_noext = file_name.split(".")[0]
	match = re.search(r"_(\d{1,2})$", file_name_noext)
	if match:
		return match.group(1)  # get last match
	else:
		return None


def get_skel_results_table_header_cols():
	# these are the columns that are in the skelresults table, we can add these to our output table if we want
	cols = [
		"NumberOfBranches",
		"NumberOfJunctions",
		"NumberOfEndpointVoxels",
		"NumberOfJunctionVoxels", 
		"NumberOfSlabVoxels",
		"AverageBranchLength", 
		"NumberOfTriplePoints", 
		"NumberOfQuadruplePoints", 
		"MaximumBranchLength", 
		"ShortestPathLength", 
		"spx", 
		"spy", 
		"spz"
		] 
	return cols


def get_output_parameters():
	output_columns = ( 
		"ImageTitle", 
		"ObjectNumber", 
		"Metadata_PlateNumber", 
		"Metadata_RowColField", 
		"Metadata_ThresholdingOP",
		"MitochondrialFootprint",
		"BranchLength_Mean",
		"BranchLength_Median",
		"BranchLength_Stdev",
		"BranchLength_Max",
		"SkeletonLength_Mean",
		"SkeletonLength_Median",
		"SkeletonLength_Stdev",
		"SkeletonLength_Max",
		"BranchesPerStructure_Mean",
		"BranchesPerStructure_Median",
		"BranchesPerStructure_Stdev",
		"BranchesPerStructure_Max",
		"Total_SkeletonLength",
		"Total_SkeletonLength_FromBranches",
		"Total_Donuts")
	header_cols = get_skel_results_table_header_cols()
	header_cols_total = ["Total_" + col for col in header_cols[:10]]  # only add totals and max for the first 11 cols since the rest are coordinates of the shortest path
	header_cols_max = ["Max_" + col for col in header_cols[:10]]
	output_columns = output_columns + tuple(header_cols_total) + tuple(header_cols_max)

	return OrderedDict((name, None) for name in output_columns)


def show_skel_results_table(skelresults, head_columns=[]):
	"""takes the skelresults object and makes a results table with the columns and values from the skelresults"""
	rt = ResultsTable()
	rt.showRowNumbers(True)

	# add index col
	if head_columns:
		head = ["Skeleton"] + head_columns
	else:
		head = ["Skeleton"] + get_skel_results_table_header_cols()

	for i in range(skelresults.getNumOfTrees()):
		rt.incrementCounter()
		rt.addValue(head[1], skelresults.getBranches()[i])
		rt.addValue(head[2], skelresults.getJunctions()[i])
		rt.addValue(head[3], skelresults.getEndPoints()[i])
		rt.addValue(head[4], skelresults.getJunctionVoxels()[i])
		rt.addValue(head[5], skelresults.getSlabs()[i])
		rt.addValue(head[6], skelresults.getAverageBranchLength()[i])
		rt.addValue(head[7], skelresults.getTriples()[i])
		rt.addValue(head[8], skelresults.getQuadruples()[i])
		rt.addValue(head[9], skelresults.getMaximumBranchLength()[i])

		# if list is poplated add these to table
		if skelresults.shortestPathList:
			rt.addValue(head[10], skelresults.getShortestPathList().get(i))
			rt.addValue(head[11], skelresults.getSpStartPosition()[i][0])
			rt.addValue(head[12], skelresults.getSpStartPosition()[i][1])
			rt.addValue(head[13], skelresults.getSpStartPosition()[i][2])

		if 0 == i % 100:
			rt.show("Results")
	rt.show("Results")
	active_window_res = wm.getActiveTable()
	active_window_res.removeNotify()
	# IJ.run("Summarize")
	# rt.show("Results")
	return rt


def analyze_skel(imp, output_parameters, out_path):
	# run AnalyzeSkeleton
	# (see https://fiji.sc/AnalyzeSkeleton
	# and https://fiji.sc/javadoc/skeleton_analysis/package-summary.html)
	skel = AnalyzeSkeleton_()
	skel.setup("", imp)
	skel_result = skel.run(AnalyzeSkeleton_.NONE, False, True, None, True, True)
	title = imp.getTitle()
	# save skelresult in a seperate dir
	secondary_dir = os.path.join(out_path, "AllSkeletons")
	# print(secondary_dir)
	if not os.path.exists(secondary_dir):
		os.mkdir(secondary_dir)
	skel_csv_filename = os.path.join(secondary_dir, title.split(".")[0] + ".csv")
	full_skel_results_table = show_skel_results_table(skel_result)
	full_skel_results_table.saveAs(skel_csv_filename)
	# read results
	shortest_paths = skel_result.getShortestPathList().toArray()
	graphs = skel_result.getGraph()
	branches = list(skel_result.getBranches())
	average_branch_lengths = list(skel_result.getAverageBranchLength())
	branch_lengths = []
	summed_lengths = []
	total_length = 0
	num_donuts = 0
	total_length_from_branches = 0
	# calculate cumulative shortest path length by summing the lengths of all the shortest paths for each skeleton

	# iterate over graphs using classes from https://github.com/StuartLab/MiNA/blob/master/src/scripts/MiNA_Analyze_Morphology.py
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
		# add summed length for this graph to the list of summed lengths for all skeletons (and update total)
		summed_lengths.append(summed_length)
		total_length += summed_length
		
 	# calculate total length from branches by multiplying the number of branches by the average branch length for each skeleton and summing across all skeletons
	for i in range(len(branches)):
		try:
			total_length_from_branches += (branches[i] * average_branch_lengths[i])
		except IndexError as e:
			print("Branch legnths out of range for image " + title + " : ")
			print(e)
			
	#get max values and handle ValueErrors for the max of an empty sequence
	try:
		max_branch_length = max(branch_lengths)
		max_skeleton_length = max(summed_lengths)
		max_branches_per_structure = max(branches)
	except ValueError as e:
		print("Image" + title + " has no valid branches, setting max values to zero. ")
		print(e)
		max_branch_length = 0
		max_skeleton_length = 0
		max_branches_per_structure = 0
		
	# update output parameters with the values we have calculated so far
	output_parameters.update({\
			"BranchLength_Mean": mean(branch_lengths),\
			"BranchLength_Median": median(branch_lengths),\
			"BranchLength_Stdev": stdev(branch_lengths),\
			"BranchLength_Max": max_branch_length,\
			"SkeletonLength_Mean": mean(summed_lengths),\
			"SkeletonLength_Median": median(summed_lengths),\
			"SkeletonLength_Stdev": stdev(summed_lengths),\
			"SkeletonLength_Max": max_skeleton_length,\
			"BranchesPerStructure_Mean": mean(branches),\
			"BranchesPerStructure_Median": median(branches),\
			"BranchesPerStructure_Stdev": stdev(branches),\
			"BranchesPerStructure_Max": max_branches_per_structure,\
			"Total_SkeletonLength": total_length,\
			"Total_SkeletonLength_FromBranches": total_length_from_branches,\
			"Total_Donuts": num_donuts,\
			}\
		)\
	# calculate totals / max and populate output parameters from the table
	columns_string = full_skel_results_table.getColumnHeadings().strip() # get rid of the index col
	columns = columns_string.split("	")
	for colname in columns[:10]:  # skip index and coordinates
		column = full_skel_results_table.getColumn(colname)
		col_total = sum(column)
		col_max = max(column)
		try:
			output_parameters["Total_" + colname] = col_total
			output_parameters["Max_" + colname] = col_max
		except KeyError:
			print("Column "+ colname + " not in output parameters, skipping total and max for this column")
			output_parameters["Total_" + colname] = None
			output_parameters["Max_" + colname] = None
	# print(str(branches) + str(median(branches))

	# Create/append results to a ResultsTable...
	morphology_tbl = tables.SimpleSheet("Mito Morphology")
	morphology_tbl.writeRow(output_parameters)
	morphology_tbl.updateDisplay()
	active_window = wm.getActiveTable()
	active_window.removeNotify()
	return imp, morphology_tbl


def calculate_footprint(imp, output_parameters):
	# calculate the mitochondrial footprint by multiplying the area of the binary image by the area fraction and then multiplying by the pixel depth to get the volume
	# uses code from MiNA_Analyze_Morphology.py
	imp_calibration = imp.getCalibration()
	frames = imp.getNFrames()
	slices = imp.getNSlices()
	binary = Duplicator().run(imp, imp.getChannel(), imp.getChannel(), 1, slices, 1, frames)
	# if you need to convert from an ImgLib2 to ImgPlus; binary = ImageJFunctions.wrap(imp, 'binary') see https://javadoc.scijava.org/ImgLib2/net/imglib2/img/display/imagej/ImageJFunctions.html
	binary.setCalibration(imp_calibration)
	binary.setDimensions(1, slices, 1)
	# Get the total_area for 2D or 3D images
	if binary.getNSlices() == 1:
		area = binary.getStatistics(Measurements.AREA).area
		area_fraction = binary.getStatistics(Measurements.AREA_FRACTION).areaFraction
		output_parameters["MitochondrialFootprint"] = area * area_fraction / 100.0
	else:
		mito_footprint = 0.0
		for slice in range(1, binary.getNSlices() + 1):
			binary.setSliceWithoutUpdate(slice)
			area = binary.getStatistics(Measurements.AREA).area
			area_fraction = binary.getStatistics(Measurements.AREA_FRACTION).areaFraction
			mito_footprint += area * area_fraction / 100.0
		output_parameters["MitochondrialFootprint"] = (mito_footprint * imp_calibration.pixelDepth)
	return output_parameters


def skeletonize_img(imp, save=False):
	# skeletonize
	IJ.run(imp, "Skeletonize (2D/3D)", "")
	# imp = IJ.getImage()
	if save:
		save_image(imp, "skeleton")
	return imp
	# run_skel(imp)


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

		# make the title attach to the required extension
		if title.endswith(extension):
			filename = title.split(".")[0]
		else:
			filename = title
		title_string = prefix + "_" + filename + "." + extension

		print(title_string)
		IJ.saveAs(imp2, extension, os.path.join(out_path, title_string))
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
		row_values = skelresults.getRow(
			i
		).values()  # this returns a dict but we only care about the numbers
		row_list = list(row_values)
		print(row_list)
		writer.writerow(row_list)
	return True


def run_script(in_path,out_path,new_filename):
	# get output parameters ready
	output_parameters = get_output_parameters()
	csv_filename = new_filename + ".csv"
	# recurse through input directory and process images, analyze skeleton, and add results to output
	for root, dirs, files in os.walk(in_path):
		for filename in files:
			if ".tiff" in filename:
				image_path = os.path.join(root, filename)
				imp = IJ.openImage(image_path)
				IJ.run(imp, "Make Binary", "")
				title = imp.getTitle()
				output_parameters.update(
					{
						"ImageTitle": title,
						"ObjectNumber": get_object_number(title),
						"Metadata_PlateNumber": get_plate_number(title,image_path),
						"Metadata_RowColField": get_location_code(title),
						"Metadata_ThresholdingOP": threshold_method,
					}
				)
				# calculate footpint before skeletonizing
				output_parameters = calculate_footprint(imp, output_parameters)
				imp = skeletonize_img(imp, save=save_images)
				imp, skelresult = analyze_skel(imp, output_parameters, out_path)
				IJ.run("Close All")
		# now export as csv
	full_csv_filename = os.path.join(out_path, csv_filename)
	skelresult.rt.save(full_csv_filename)
	print("Saved at " + os.path.join(out_path, csv_filename))
	# IJ.selectWindow("Mito Morphology")
	# IJ.saveAs("Results", os.path.join(out_path,csv_filename))

	# cleanup
	IJ.run("Clear Results")
	wm.getWindow("Mito Morphology").close()
	wm.getWindow("Results").close()

def batch_run_script(in_path,out_path):
	# Replacing some abbreviations (e.g. $HOME on Linux).
	print(in_path)
	in_path = os.path.expanduser(in_path)
	in_path = os.path.expandvars(in_path)
	folders_to_use = []
	#add all folders to dir
	for item in os.listdir(in_path):
		#make the correct path and add to dir if this is a dir
		full_path = os.path.join(in_path, item)
		if os.path.isdir(full_path):
			
			folders_to_use.append(full_path)
	#now run script for everything in listy
	for folder in folders_to_use:
		abspath_folder = os.path.abspath(folder)
		foldername = os.path.basename(folder)
		new_out_folder = os.path.join(out_path,foldername)
		print("Running through folder: "+ foldername + ", full path: "+ abspath_folder + "; saving to: "+ new_out_folder)
		if not os.path.exists(new_out_folder):
			os.mkdir(new_out_folder)
		run_script(abspath_folder,new_out_folder,foldername)

if __name__ in ["__builtin__", "__main__"]:
	in_path = in_dir.getAbsolutePath()
	out_path = out_dir.getAbsolutePath()
	new_filename = in_dir.getName()
	if batch_folder:
		batch_run_script(in_path,out_path)
	else:
		run_script(in_path,out_path,new_filename)
