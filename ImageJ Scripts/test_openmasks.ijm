#@ File (style="directory") image_fold

run("/mnt/bigdisk1/AllieSpangaro/Scripts/imageJ_macros/ImageJ Scripts/OpenMaxProjImage_Phenix.ijm");
title = getTitle();
old_mask_file_path = image_fold + File.separator + "newmasks" + File.separator + title + "_v2_cell_masks.tif";
print(old_mask_file_path);

/*
open("/mnt/bigdisk1/AllieSpangaro/Morphology_Replicative_Age_Project/MRC-5_MAX_SUM_PROJ/20250501_rep07/newmasks/r02c01f01_nuclei_masks.tif");
selectImage("r02c01f01_nuclei_masks.tif");
open("/mnt/bigdisk1/AllieSpangaro/Morphology_Replicative_Age_Project/MRC-5_MAX_SUM_PROJ/20250501_rep07/testmasks/rep07_r02c01f01_cell_cpsam_v2_masks.tif");
selectImage("rep07_r02c01f01_cell_cpsam_v2_masks.tif");
close;
open("/mnt/bigdisk1/AllieSpangaro/Morphology_Replicative_Age_Project/MRC-5_MAX_SUM_PROJ/20250501_rep07/testmasks/rep07_r02c01f01_nuclei_cpsam_v2_masks.tif");
selectImage("rep07_r02c01f01_nuclei_cpsam_v2_masks.tif");
selectImage("r02c01f01_nuclei_masks.tif");
selectImage("rep07_r02c01f01_nuclei_cpsam_v2_masks.tif");
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
