#@ File (style="open") inputFile
#@ File (style="directory") outFolder
#@ String (default="tiff") extension
#@ boolean fill_holes
#@ boolean closing
#@ String prefix
open(inputFile);
filename = File.nameWithoutExtension;
title = getTitle();
Image.removeScale;
run("Enhance Contrast", "saturated=0.35");
run("Duplicate...", " ");
run("Subtract Background...", "rolling=9");
run("Gray Scale Attribute Filtering", "operation=Opening attribute=Area minimum=24 connectivity=4");
run("Enhance Contrast", "saturated=0.35");
waitForUser("Click ok when done");
setOption("ScaleConversions", true);
run("Enhance Contrast...", "saturated=0.0 normalize process_all use");
run("8-bit");
run("Auto Threshold", "method=Huang2 white");
//run("Auto Local Threshold", "method=Bernsen radius=15 parameter_1=0 parameter_2=0 white");
if(closing){
	run("Binary Morphological Filters", "operation=Closing radius=1");
	}
if(fill_holes){
	run("Fill Holes");
}

run("Set Measurements...", "area mean standard perimeter shape feret's integrated median redirect=None decimal=3");
//run("Connected Components Labeling", "connectivity=4 type=[16 bits]");
run("Label Splitter (2D/3D)", "separationmethod=[DoG Seeds] spotsigma=1.0 maximaradius=2.0 stackslice=1 processonthefly=false");
run("8-bit");
labelTitle = getTitle();
run("Labels to 2D Roi Manager", "process_all_slices=true");
roiManager("measure");
resultsTitle = Table.title;
saveAs("Results", outFolder+File.separator+filename+"_"+resultsTitle+".csv");
close(resultsTitle);
selectImage(title);
run("8-bit");
run("Select All");
roiManager("Show All without labels");
run("Flatten");
//run("Binary/Labels Overlay");
overlayTitle = getTitle();
saveAs(extension, outFolder+File.separator+prefix+overlayTitle);

selectImage(labelTitle);
saveAs(extension, outFolder+File.separator+prefix+labelTitle);


waitForUser("Click ok when done");

close("*");
