#@ File (label = "Image directory", style = "directory") input_imgs
#@ File (label = "ROI directory", style = "directory") input_rois
#@ File (label = "Output directory", style = "directory") output
#@ String(choices={".zip", "None"}, style="list") rois_ext
#@ String (label = "Mask Image Suffix", value = "_masks") mask_suffix
#@ String (label = "Mask Image Extension", value = ".tiff") img_ext


function processRoiFolder(input_rois) {
	list = getFileList(input_rois);
	list = Array.sort(list);
	
	img_list = getFileList(input_imgs);
	img_list = Array.sort(img_list);
	
	if(img_list.length != list.length){
		print("Error, lists are not equal length, ROIs don't match imgs");
		return()
	}
	
	setBatchMode("hide");
	
	for (i = 0; i < list.length; i++) {
		//go thru all the ROIs
		print(input_rois + File.separator);
		showProgress(i, list.length);
		if(File.isDirectory(input_rois + File.separator + list[i]))
			processFolder(input_rois + File.separator + list[i]);
		//process the ROI (default is zip)
		if(endsWith(list[i], rois_ext))
			imageTitle = img_list[i];
			saveCellposeRoi(input_rois, input_imgs, output, list[i], imageTitle);
	}
	setBatchMode("show");
}
/*
function getImageTitle(img_folder, output, roi_file_path, img_ext){
	//get the corresponding image based on filename of ROI zip file
	if(!endsWith(roi_file_path, rois_ext)){
		roi_file_path = roi_file_path + rois_ext;
	}
	roi_file_title = File.getNameWithoutExtension(roi_file_path);
	roi_file_split = split(roi_file_title, "_");
	roi_split_nosuffix = roi_file_split[:roi_file_split.length];
	
	img_title = String.join(roi_split_nosuffix);
	if(endsWith(img_title, "cpsam_v2") || endsWith(img_title, "cpdino")){
		roi_file_split = split(roi_file_title, "_");
		roi_split_nomodel= roi_file_split[:roi_file_split.length];
	
		img_title = String.join(roi_split_nosuffix);
	}
	img_path = output + File.separator + img_title + img_ext;
	
}
*/
function saveCellposeRoi(input_rois, input_imgs, output, rois_title, img_title) {
	roiManager("reset");
	open(input_imgs + File.separator + img_title);
	roiManager("Open", input_rois + File.separator + rois_title);
	setOption("ScaleConversions", true);
	run("ROIs to Label image");
	mask_image_title = "ROIs2Label_" + img_title;
	selectImage(mask_image_title);
	
	img_title_noext = File.getNameWithoutExtension(img_title);
	
	if(endsWith(img_title_noext, mask_suffix)){
		new_mask_img_title = img_title_noext + img_ext;
	}
	else{
		new_mask_img_title = img_title_noext + mask_suffix + img_ext;
	}

	mask_img_path = output + File.separator + new_mask_img_title;
	print("Saving masks to: " + mask_img_path);
	saveAs("tif", mask_img_path);
	
	close("*");
	
}
processRoiFolder(input_rois);