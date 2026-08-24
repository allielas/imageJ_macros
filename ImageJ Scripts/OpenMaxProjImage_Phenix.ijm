/*
 * Macro to open a specified image from a folder using a rXXcYYfZZ well plate coordinate scheme 
 */
 

macro "OpenMaxProjImage_Phenix"{
#@ File (label = "Input directory", style = "directory") input
#@ String (label = "File extension suffix", value = ".tif") suffix
#@ int (min=1, max=16, style="slider") row 
#@ int (min=1, max=24, style="slider") col 
#@ int (min=1, max=40, style="slider") field
#@ String(label="What is your fluorescence channel order", description="Enter colors in order seperated by commas e.g. green,red,far red,blue") channelOrder
#@ boolean (label = "Using DPC?") DPC
#@ boolean (label = "Open random image instead?") randomFlag


//Fix stupid UI bug that doesn't save the default value
	if(row < 1){
		row = 1
	}
	if(col < 1){
		col = 1
	}
	if(field < 1){
		field = 1
	}
	
	//add the file separator satisfy linux path
	input = input+ File.separator;
	
	channelColours = split(channelOrder,",");
	nChannels = lengthOf(channelColours);
	//print(nChannels);
	
	if(randomFlag == 1){
		//open random if flagged, else 
		openRandomImage(input,suffix);
	}
	else{
		openImage(input,suffix);
	}
	
	function makeCoordinateString(row,col,field) { 
	// convert the integers into the Harmony RowColField syntax
		rowString = convertNumberTo2DigitString(row);
		colString = convertNumberTo2DigitString(col);
		fieldString = convertNumberTo2DigitString(field);
		rowcolfield = "r" + rowString + "c" + colString + "f" + fieldString;
		return rowcolfield;
	}
	
	function convertNumberTo2DigitString(number) { 
	// convert a number to a two digit string, with a prefix 0 added to numbers below 10
		if (number < 10){ 
			number = "0" + number;
			}	
		return "" + number;
	}
	
	function openImage(input,suffix) { 
	// opens an image at specified rowcolfield 
		rowcolfield = makeCoordinateString(row,col,field);
		merge_ch(input,rowcolfield,suffix,nChannels);
	}
	
	
	function openRandomImage(input,suffix) { 
	// calls the random_image_rowcol function and opens the image
		rowcolfield = random_image_rowcolfield(input);
		merge_ch(input,rowcolfield,suffix,nChannels);
	}
	
	function scanFolder(input) {
		list = getFileList(input);
		list = Array.sort(list);
		for (i = 0; i < list.length; i++) {
			if(File.isDirectory(input + File.separator + list[i]))
				scanFolder(input + File.separator + list[i]);
			//if(endsWith(list[i], suffix))
				//processFile(input, output, list[i]);
		}
	}
	
	function random_image_rowcolfield(input) {
	//add a randomzie function to pick random files from the file list in the specified folder
		list = getFileList(input);
		rand = ""+round(list.length * random);
		filename = list[rand];
		rowcolfield = substring(filename, 8, 17);
		return rowcolfield;
	}
	function colour_rename(channelColours){
		//rename colours to add flexibility

		for (i = 0; i < channelColours.length; i++) {
			colour = toLowerCase(channelColours[i]);
			if (colour == "g" || colour=="gfp" || colour=="488"){
					colour = "green";
			}
			else if (colour == "r" || colour=="rfp" || colour=="cy3"){
				colour = "red";
	
			}
			else if (colour == "b" || colour == "dapi"){
				colour = "blue";
	
			}
			else if (colour == "far-red" || colour == "farred" || colour=="far red" || colour=="cy5" || colour=="647") {
				colour = "fr";
			}
			channelColours[i] = colour;
			//Array.print(channelColours);
		}
		
	}
	
	function get_colour_index(colour){
		//define colours based on your image channels, returns the index of your colour value
		colour_index=-1;
		for(i=0; i< channelColours.length; i++){
			//print(colour + " " + i+  " , "+ colour_index);
			// assign if you get the match
			if(channelColours[i]== colour){
				//print(colour + " , "+ colour_index);
				colour_index = i;
			}
		}
		
		if(colour_index==-1)
		{
			//Array.print(channelColours);
			exit("colour " + colour + " not found");
		}
		return colour_index
	}
	function merge_ch(path,rowcolfield,suffix,channels) {
		// function to open each single-channel image from that location and merge into a color composite
	
		colour_rename(channelColours);
	
		// We allow a flexible prefix before "MAX_ch{N}-{rowcolfield}{suffix}"
		// Example match: "*MAX_ch2-r01c01f01.tif"
		function findFileWithSuffixAndPattern(dir, chIndex) {
			// Build the required "tail" that must match exactly
			// (everything before this tail is the flexible/wildcard part)
			tail = "MAX_ch" + chIndex + "-" + rowcolfield + suffix;
	
			list = getFileList(dir);
			for (k = 0; k < list.length; k++) {
				// match filename that ends with the required tail
				// (this is your wildcard-at-start behavior)
				if (endsWith(list[k], tail)) {
					return dir + list[k];
				}
			}
			return "";
		}
	
		// Determine channel index range
		startIndex = 1;
		endIndex = channels;
		if (DPC) {
			startIndex = 2;
			endIndex += 1;
		}
	
		// Make sure channel 1 exists (using wildcard matching)
		testPath = findFileWithSuffixAndPattern(path, 1);
		if (lengthOf(testPath) == 0) {
			exit("Error: File not found at the plate coordinates: " + rowcolfield + "\nin directory: \n" + path);
		}
			
		// Open in order by channels
		for (i = startIndex; i <= endIndex; i++) {
			curr_img_path = findFileWithSuffixAndPattern(path, i);
			if (lengthOf(curr_img_path) == 0) {
				exit("Error: Missing file for channel " + i + " at " + rowcolfield + "\nin directory: \n" + path);
			}
			
			open(curr_img_path);
		}
	
		pre_chNames = getList("image.titles"); // 0-indexed list of open image titles
		if (pre_chNames.length > 4) {
			// If more than 4 images, only take the last 4
			extra_images = pre_chNames.length - 4;
			//print("there are " + pre_chNames.length + " open images, skipping first " + extra_images+ ".");
			chNames = Array.slice(pre_chNames,extra_images,pre_chNames.length);
		}
		else{
			chNames = pre_chNames;
		}
	
		if(nChannels == 3) {
			run("Merge Channels...", "red="+ chNames[get_colour_index("red")] +
				" green="+ chNames[get_colour_index("green")] +
				" c5="+ chNames[get_colour_index("blue")] +
				" create");
		} else {
			run("Merge Channels...", "red=" + chNames[get_colour_index("red")] +
				" green=" + chNames[get_colour_index("green")] +
				" c5=" + chNames[get_colour_index("blue")] +
				" c6=" + chNames[get_colour_index("fr")] +
				" create");
		}
	
		// change image name to avoid confusion + add the plate number to filename
		
		//get rep string (rep0X) from path
		//input_folder_split = split(File.getName(input), "_");
		input_folder_split = split(input, File.separator+"_");
		//Array.print(input_folder_split);
		rep = Array.filter(input_folder_split,"(rep\\d{2}\\z)");
		Array.show(rep);
		// go through the matches and rename with first one
		if (lengthOf(rep) > 0){
			for (i=0; i< lengthOf(rep); i++){
				if (startsWith(rep[i], "rep")){
					rename(rep[i]+ "_" +rowcolfield);
					break
				}
			}
		}
		else {
			rename(rowcolfield);
		}
	}

}
