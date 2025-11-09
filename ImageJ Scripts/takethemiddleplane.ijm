
outFolder = "/mnt/bigdisk1/AllieSpangaro/Senesence_Markers_Classification/Pilot_IndivChannels"

run("Make Composite");
run("Reduce Dimensionality...", "channels keep");
title = getTitle();
for (i = 1; i <= nSlices; i++) {
    setSlice(i);
    run("Enhance Contrast", "saturated=0.35");
    if(i==1){
		run("Green");
		setMinAndMax(250, 6000);
	}
	else if(i==2){
		run("Cyan");
	}
	else if(i==3){
		run("Magenta");
		run("Enhance Contrast", "saturated=0.35");
	}
	else if(i==4){
		run("Grays");
		setMinAndMax(100, 1000);
	}
}
saveAs("Tiff", outFolder+"/"+title+".tif");
close();
