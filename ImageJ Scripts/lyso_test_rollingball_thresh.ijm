#@ File (style="open") inputFile
open(inputFile);

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
//run("Binary Morphological Filters", "operation=Closing radius=2");
run("Fill Holes");
run("Set Measurements...", "area mean standard perimeter shape feret's integrated median redirect=None decimal=3");
//run("Connected Components Labeling", "connectivity=4 type=[16 bits]");
run("Label Splitter (2D/3D)", "separationmethod=[DoG Seeds] spotsigma=1.0 maximaradius=2.0 stackslice=1 processonthefly=false");
run("Labels to 2D Roi Manager", "process_all_slices=true");
//run("Analyze Particles...", "size=20-Infinity exclude clear add");
selectImage(title);
run("8-bit");
run("Select All");
roiManager("Show All without labels");
//run("ROIs to Label image");
//labelTitle = getTitle();
//run("Draw Labels As Overlay", "label="+labelTitle+" image="+title+" x-offset=-5 y-offset=-5");
//run("Binary/Labels Overlay");
waitForUser("Click ok when done");

close("*");