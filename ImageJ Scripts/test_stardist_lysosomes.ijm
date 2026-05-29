//#@ String directory
#@ File (style="open") inputFile

probThresh = "0.3";
overlapLevel = "0.4";

open(inputFile);
//open(directory + File.separator + "dummy.tiff");
run("Morphological Filters", "operation=[White Top Hat] element=Disk radius=15");
//saveAs("tiff", directory+File.separator+"tophat.tiff");
title = getTitle();

run("Command From Macro", "command=[de.csbdresden.stardist.StarDist2D], args=['input':'"+title+"', 'modelChoice':'Versatile (fluorescent nuclei)', 'normalizeInput':'true', 'percentileBottom':'1.0', 'percentileTop':'99.8', 'probThresh':'0.30000000000000004', 'nmsThresh':'0.4', 'outputType':'ROI Manager', 'nTiles':'1', 'excludeBoundary':'2', 'roiPosition':'Automatic', 'verbose':'false', 'showCsbdeepProgress':'false', 'showProbAndDist':'false'], process=[false]");
run("ROIs to Label image");
//selectImage("ROIs2Label_"+title);
//saveAs(directory+File.separator+"outlines.tiff");
//exit();