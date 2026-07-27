#@ File (style="directory") inputFolder
#@ File (style="directory") outFolder
#@ String (label = "File suffix", value = ".tif") extension
#@ String chNumber
#@ boolean fill_holes
#@ boolean closing

function processFolder(inputFolder) {
	list = getFileList(inputFolder);
	list = Array.sort(list);
	//setBatchMode(true);

	for (i = 0; i < list.length; i++) {
		//print(list[i]);
		if(File.isDirectory(inputFolder + File.separator + list[i])){
			processFolder(inputFolder + File.separator + list[i]);
		}
		if(endsWith(list[i], extension)){
			run("ROI Manager...");
			roiManager("reset");
			channel = "ch"+chNumber;
			thisFile=list[i];
			if(thisFile.contains(channel)){ 
				processFile(inputFolder, outFolder, thisFile);

			}
		}
	}
	//setBatchMode(false);
}

function processFile(inputFolder, outFolder, file) {
	open(inputFolder + File.separator + file);
	filename = File.nameWithoutExtension;
	title=getTitle();
	Image.removeScale;
	run("Enhance Contrast", "saturated=0.35");
	run("Duplicate...", " ");
	run("Subtract Background...", "rolling=9");
	run("Gray Scale Attribute Filtering", "operation=Opening attribute=Area minimum=24 connectivity=4");
	run("Enhance Contrast", "saturated=0.35");
	setOption("ScaleConversions", true);
	run("Enhance Contrast...", "saturated=0.0 normalize process_all use");
	run("8-bit");
	run("Auto Threshold", "method=Huang2 white");

	if(closing){
		run("Binary Morphological Filters", "operation=Closing radius=1");
		}
	if(fill_holes){
		run("Fill Holes");
	}
	
	run("Set Measurements...", "area mean standard perimeter shape feret's integrated median redirect=None decimal=3");
	run("Label Splitter (2D/3D)", "separationmethod=[DoG Seeds] spotsigma=1.0 maximaradius=2.0 stackslice=1 processonthefly=false");
	
	run("8-bit");
	saveAs(extension, outFolder+File.separator+"Labels_"+filename+"."+extension);
	run("ROI Manager...");
	run("Labels to 2D Roi Manager", "process_all_slices=true");
	selectImage(title);
	roiManager("measure");
	resultsTitle = Table.title;
	saveAs("Results", outFolder+File.separator+filename+"_"+resultsTitle+".csv");
	run("8-bit");
	//run("Select All");
	roiManager("show all without labels");
	updateDisplay();
	run("Flatten");
	saveAs(extension, outFolder+File.separator+"Overlay_"+filename+"."+extension);
	
	//resultsTitle = Table.title;
	close("*");
	close("ROI Manager");
	run("Clear Results");
	close(resultsTitle);
}


processFolder(inputFolder);