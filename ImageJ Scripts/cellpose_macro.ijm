#@ File(style="directory" , label="Select conda environment") conda_env_path
#@ String(choices={"cpsam_v2", "cpsam", "cpdino", "cpdino_vitb"}, style="list") model
#@ File (label = "Input directory", style = "directory") input
#@ File (label = "Output directory", style = "directory") output
#@ String(label = "Choose what to save:", choices={"mask_images", "rois", "both"}, style="list") save_type
#@ String (label = "File suffix", value = ".tiff") suffix

//run("Blobs (25K)"); // uncomment to test

function processFolder(input) {
	list = getFileList(input);
	list = Array.sort(list);
	setBatchMode("hide");
	
	for (i = 0; i < list.length; i++) {
		print(input + File.separator);
		showProgress(i, list.length);
		if(File.isDirectory(input + File.separator + list[i]))
			processFolder(input + File.separator + list[i]);
		if(endsWith(list[i], suffix))
			runCellpose(input, output, list[i]);
	}
	setBatchMode("show");
}

function runCellpose(input, output, file) {
	// Do the processing here by adding your own code.
	// Leave the print statements until things work, then remove them.
	roiManager("reset");
	open(input + File.separator + file);
	image_title = getTitle();
	image_title_noext = File.getNameWithoutExtension(image_title);

	run("Cellpose SAM..." ,"imp="+image_title+" env_path="+conda_env_path+" env_type=conda model="+model+" model_path= diameter=None additional_flags=--use_gpu" );

	//get cellpose img
	mask_img = File.getNameWithoutExtension(image_title)+"-cellpose";
	selectImage(mask_img);
	//get the new title to not have the "-cellpose" innit
	new_mask_img_title = image_title_noext + "_masks";
	
	if(save_type == "mask_images" || save_type == "both"){
		mask_img_path = output + File.separator + new_mask_img_title + suffix;
		print("Saving masks to: " + mask_img_path);
		saveAs("tif", mask_img_path);
	}
	if(save_type == "rois" || save_type == "both"){
		roi_path = output + File.separator + image_title_noext + "_RoiSet.zip";
		saveROIs(new_mask_img_title, roi_path);
	}
	close("*");
	
}

function saveROIs(img, roi_path) { 
// function description
	if(!endsWith(img, suffix)){
		img = img + suffix;
	}
	selectImage(img);
	run("Label image to ROIs", "rm=[RoiManager[size=95, visible=false]]");
	nROIs = roiManager("count");
	if(nROIs > 0) {
		print("Saving ROIs to: " + roi_path);
		roiManager("Save", roi_path);
	}
	else{
		print("ROI list for "+File.getNameWithoutExtension(img)+" is empty");
	}
}

processFolder(input);