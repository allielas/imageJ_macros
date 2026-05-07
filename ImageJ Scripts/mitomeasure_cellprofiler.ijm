#@ String directory
#@ Integer(value=1, min=0, max=5) unsharp_radius
#@ Float (value=0.60, min=0.0, max=5.0) unsharp_weight 
#@ Integer(value=127, min=0, max=1024) clahe_block
#@ Integer(value=256, min=0, max=1024) clahe_bins
#@ Integer(value=3, min=0, max=24) clahe_slope

setBatchMode("hide");
/*
function threshold(imp, method_threshold="Otsu",relative_threshold="1"):
	//Get the histogram
	histo = ops.run("image.histogram");
	//Get the threshold
	threshold_value = ops.run("threshold.%s" % method_threshold, histo);
	//Modulate "threshold_value" by "relative_threshold"
	threshold_value = int(round(threshold_value.get() * relative_threshold));
	//We should not have to do that...
	threshold_value = UnsignedByteType(threshold_value);
	//Apply the threshold
	thresholded = ops.run("threshold.apply", data, threshold_value);
	return thresholded;
*/
//open image
//if using CP, assumes you are giving it a single-channel image
open(directory+File.separator+"dummy.tiff"); //note that dummy.tiff is the input image filename for cp, and "directory" is the directory variable
//run("Median...", "radius="+median_radius+""); !!!NOTE: DO NOT USE MEDIAN FILTER for CP, will crash
run("Unsharp Mask...", "radius="+unsharp_radius+" mask="+unsharp_weight+"");      
//run("Enhance Local Contrast (CLAHE)", "blocksize="+clahe_block+" histogram="+clahe_bins+" maximum="+clahe_slope+" mask=*None* fast_(less_accurate)");
run("Enhance Local Contrast (CLAHE)", "blocksize=127 histogram=256 maximum=3 mask=*None* fast_(less_accurate)");
saveAs("tiff",directory+File.separator+"preprocessed.tiff");
//selectImage(preprocessed);
//threshold and skeletonize
setAutoThreshold("Otsu dark 16-bit no-reset"); 
setOption("BlackBackground", true); //Prefs.blackBackground = True;
run("Make Binary","");
//run("Open", "");
saveAs("tiff",directory+File.separator+"threshmito.tiff");
//run("Skeletonize", "");
///saveAs("tiff",directory+File.separator+"skelmito.tiff");
//run("Analyze Skeleton (2D/3D)", ""); //prune=[shortest branch] prune_0 calculate
exit();
run("System.exit(1)");