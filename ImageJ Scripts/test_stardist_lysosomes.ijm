#@ File (style="open") inputFile
probThresh = "0.3";
overlapLevel = "0.4";

open(inputFile);
title = getTitle();
run("Morphological Filters", "operation=[White Top Hat] element=Disk radius=15");
run("Command From Macro", "command=[de.csbdresden.stardist.StarDist2D], args=['input':'"+title+"', 'modelChoice':'Versatile (fluorescent nuclei)', 'normalizeInput':'true', 'percentileBottom':'1.0', 'percentileTop':'99.8', 'probThresh':'"+probThresh+"', 'nmsThresh':'"+overlapLevel+"', 'outputType':'Both', 'nTiles':'1', 'excludeBoundary':'2', 'roiPosition':'Automatic', 'verbose':'false', 'showCsbdeepProgress':'false', 'showProbAndDist':'false'], process=[false]");
