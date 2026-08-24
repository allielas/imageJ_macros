#@ File (style="directory") image_fold
#@ File (style="directory") output_folder
#@ Integer (value=324, min=128, max=4060, style="slider", persist=false) scale


run("OpenMaxProjImage Phenix", "input="+image_fold);
title = getTitle(); //use title to open correct masks
//print(title);
//get rep string (rep0X) from path or filename, whichever works
if (startsWith(title, "rep")){
	rep_arr = split(title, "_"); //e.g rep05_r02c02f02
	rep = rep_arr[0];
	//make a new title for compatibility
	path_title = rep_arr[1];
}
else {
	rep_arr = split(File.getName(image_fold), "_"); //e.g. .../20260504_rep02
	rep = rep_arr[1];
	path_title=title;
}

//rescale and up intensity of slices
run("Scale...", "x=- y=- width="+scale+" height="+scale+" interpolation=Bicubic average create");
for (i = 1; i < nSlices; i++) {
    setSlice(i);
    run("Enhance Contrast", "saturated=0.35");
}
saveAs("png", output_folder + File.separator + rep + "_" + path_title + "_composite.png");
close(title);

//print(rep);

// old masks
old_cell_mask_file_path = image_fold + File.separator + "newmasks" + File.separator + path_title + "_v2_cell_masks.tif";
old_nuc_mask_file_path = image_fold + File.separator + "newmasks" + File.separator + path_title + "_nuclei_masks.tif";

//old test masks cpsam_v2
new_cell_mask_file_path = image_fold + File.separator + "testmasks" + File.separator + rep + "_" + path_title + "_cell_cpsam_v2_masks.tif";
new_nuc_mask_file_path = image_fold + File.separator + "testmasks" + File.separator + rep + "_" + path_title + "_nuclei_cpsam_v2_masks.tif";

//new masks cpsam_v2
cpsamv2_cell_mask_file_path = image_fold + File.separator + "testmasks_cpsam_v2" + File.separator + rep + "_" + path_title + "_cell_cpsam_v2_masks.tif";
cpsamv2_nuc_mask_file_path = image_fold + File.separator + "testmasks_cpsam_v2" + File.separator + rep + "_" + path_title + "_nuclei_cpsam_v2_masks.tif";

//new masks cpdino
dino_cell_mask_file_path = image_fold + File.separator + "testmasks_cpdino" + File.separator + rep + "_" + path_title + "_cell_cpdino_masks.tif";
dino_nuc_mask_file_path = image_fold + File.separator + "testmasks_cpdino" + File.separator + rep + "_" + path_title + "_nuclei_cpdino_masks.tif";



masks_paths = newArray(old_cell_mask_file_path,old_nuc_mask_file_path,new_cell_mask_file_path,new_nuc_mask_file_path,cpsamv2_cell_mask_file_path,cpsamv2_nuc_mask_file_path,dino_cell_mask_file_path,dino_nuc_mask_file_path);

if (masks_paths.length %2 ==0){
	montage_rows = masks_paths.length / 2;
}
else {
	print("ERROR: uneven number of masks detected, found "+ masks_paths.length + " masks");
	montage_rows = 3
}

for (i = 0; i < masks_paths.length; i++) {
    open(masks_paths[i]);
    current_img = getTitle();
    
    //put path parent in title to fix name conflicts
    parent = File.getParent(masks_paths[i]);
    parent_name=File.getName(parent);
    new_title = parent_name + "_" + current_img;
    
    rename(new_title);
    run("3-3-2 RGB");
    run("Scale...", "x=- y=- width="+scale+" height="+scale+" interpolation=Bilinear average create");
    close(new_title);
}
run("Images to Stack", "use");
run("Make Montage...", "columns=2 rows="+ montage_rows +" scale=1 border=2 label");
saveAs("png",output_folder + File.separator + rep + "_" + path_title + "_masks_montage.png");
waitForUser("Close images when done");
close("*");
//close("Stack");
/*
open("/mnt/bigdisk1/AllieSpangaro/Morphology_Replicative_Age_Project/MRC-5_MAX_SUM_PROJ/20250501_rep07/newmasks/r02c01f01_nuclei_masks.tif");
selectImage("r02c01f01_nuclei_masks.tif");
open("/mnt/bigdisk1/AllieSpangaro/Morphology_Replicative_Age_Project/MRC-5_MAX_SUM_PROJ/20250501_rep07/testmasks/rep07_r02c01f01_cell_cpsam_v2_masks.tif");
selectImage("rep07_r02c01f01_cell_cpsam_v2_masks.tif");
close;
open("/mnt/bigdisk1/AllieSpangaro/Morphology_Replicative_Age_Project/MRC-5_MAX_SUM_PROJ/20250501_rep07/testmasks/rep07_r02c01f01_nuclei_cpsam_v2_masks.tif");
selectImage("rep07_r02c01f01_nuclei_cpsam_v2_masks.tif");
selectImage("r02c01f01_nuclei_masks.tif");
selectImage("rep07_r02c01f01_nuclei_cpsam_v2_masks.tif");/mnt/bigdisk1/AllieSpangaro/Scripts/imageJ_macros/ImageJ Scripts/OpenMaxProjImage_Phenix.ijm
run("Scale...", "x=- y=- width=540 height=540 interpolation=Bicubic average create");
selectImage("rep07_r02c01f01_nuclei_cpsam_v2_masks.tif");
close;
run("OpenMaxProjImage Phenix");
open("/mnt/bigdisk1/AllieSpangaro/Scripts/imageJ_macros/ImageJ Scripts/OpenMaxProjImage_Phenix.ijm");
run("script:/mnt/bigdisk1/AllieSpangaro/Scripts/imageJ_macros/ImageJ Scripts/OpenMaxProjImage_Phenix.ijm", "  input=/mnt/bigdisk1/AllieSpangaro/Morphology_Replicative_Age_Project/MRC-5_MAX_SUM_PROJ/20250328_rep05 suffix=.tif row=2 col=1 field=1 channelorder=gfp,rfp,fr,dapi dpc=false randomflag=false");
selectImage("MAX_ch3-r02c01f01.tif");
selectImage("MAX_ch2-r02c01f01.tif");
selectImage("MAX_ch1-r02c01f01.tif");
selectImage("rep07_r02c01f01_nuclei_cpsam_v2_masks-1.tif");
close;
selectImage("r02c01f01_nuclei_masks.tif");
close;
close;
close;
close;
selectImage("MAX_ch4-r02c01f01.tif");
close;
*/
