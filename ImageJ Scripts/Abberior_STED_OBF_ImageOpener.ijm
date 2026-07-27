#@ File (style="open") inputFile
#@ String(choices={"Overview", "STED Selection"}, style="list") ROItype

if(ROItype == "STED Selection"){
	run("Bio-Formats Importer", "open=["+inputFile+"] autoscale color_mode=Default rois_import=[ROI manager] view=Hyperstack stack_order=XYCZT series_5 series_6");
}
else if (ROItype == "Overview"){
	run("Bio-Formats Importer", "open=["+inputFile+"] autoscale color_mode=Default rois_import=[ROI manager] view=Hyperstack stack_order=XYCZT series_1 series_3");
}
//selectImage("IMG0184_P20.obf - STAR ORANGE.STED");
//selectImage("IMG0184_P20.obf - STAR RED.STED");
imgs = getListOfImages();

run("Merge Channels...", "c1=["+imgs[0]+"] c4=["+imgs[1]+"] create");

run("Enhance Contrast", "saturated=0.35");
run("Red Hot");
waitForUser("Press OK when done counting");
run("Select None");
close("*");