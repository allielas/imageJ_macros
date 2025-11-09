#@ File (style="directory") imageFolder
#@ File (style="directory") outFolder

filelist = getFileList(imageFolder);

function setContrast(fileName) { 
	resetMinAndMax;
    run("Enhance Contrast", "saturated=0.35");
    if(fileName.contains("488")){
		setMinAndMax(250, 6000); // Set min and max to a set value for channel 2 (GFP) (used 200, 1000 for p16)
	}
	else if(fileName.contains("568")){
		setMinAndMax(250, 6000); // Set min and max to a set value for channel 2 (GFP) (used 200, 1000 for p16)
	}
}

for (i = 0; i < lengthOf(filelist); i++) {
	setBatchMode(true);
    if (endsWith(filelist[i], ".tiff")) {   //This directs the program to the folder to use.
    	fileName = filelist[i];
    	//print(fileName);
    	open(imageFolder + "/" + fileName);
    	original=getTitle();
    	splitFileName = split(original,".");
    	fileName_noext = splitFileName[0];
		selectWindow(original);
		run("Select None");
	    //first square
		run("Duplicate...", " ");
		selectImage(fileName_noext+"-1.tiff");
		makeRectangle(23296, 0, 8025, 6048);
		roiManager("Add");
		run("Crop");
		setContrast(fileName_noext);
		saveAs("Tiff", outFolder+"/"+fileName_noext+"_A.tif");
		
		//second_square
		selectImage(original);
		makeRectangle(0, 23296, 8025, 6048);
		run("Crop");
		setContrast(fileName_noext);
		saveAs("Tiff", outFolder+"/"+fileName_noext+"_B.tif");
		//Go to next image in folder and start again:
		close("*");
		//close("\\Others");	//This closes all the inactive image(s) without closing the Results window or the ROI Manager
		
    }
		
}