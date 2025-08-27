#@ File (style="directory") imageFolder
#@ File (style="directory") outputFolder


macro "ROI crop [6] "{   //Assigns '7' as shortcut to run macro.
//Getting set up for the session

	//dir = File.directory;
	filelist = getFileList(imageFolder); 
	for (i = 0; i < lengthOf(filelist); i++) {
	    if (endsWith(filelist[i], ".vsi")) {   //This directs the program to the folder to use.
	    	fileName = filelist[i];
	    	//print(fileName);
	    	open(imageFolder + "/" + fileName);
	    	original=getTitle();
			selectWindow(original);
			run("Select None"); //Removes any ROIs that may have been left from the previous image.
				//returns string with the image title, which is the original image. 
			//ID'g it here so it can be called again at the end in order to move to the next image in the folder
			//Preparing area to be measured
			for (j = 1; j <= nSlices; j++) {
		    	setSlice(j);
		    	run("Enhance Contrast", "saturated=0.35");
		    	//run("Enhance Local Contrast (CLAHE)", "blocksize=127 histogram=256 maximum=3 mask=*None* fast_(less_accurate) process_as_composite");
		    	//if(j==(gfpChannel)){
		    	//	setMinAndMax(800, 20000); // Set min and max to a set value for channel 2 (GFP) (used 200, 1000 for p16)
		    	//}
		    }
			makeRectangle(686, 683, 800, 800);
			waitForUser("Move your ROI");
			roiManager("add & draw");
			run("Crop");
			//save(dir + "/crops/" + zproj_name +"_crop.tif");
			save(outputFolder + "/" + original + "_crop.tif");
			//Go to next image in folder and start again:
			//selectWindow(original);	//This selects the original image, with the filename so that 'Open next' will have a reference of what was previously open so it knows where to go next.
			selectWindow(original);
			close("*");
			//close("\\Others");	//This closes all the inactive image(s) without closing the Results window or the ROI Manager
	    }
			
	}
	roiManager("save", outputFolder);
}
