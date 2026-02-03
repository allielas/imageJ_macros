#@ File (label = "Input directory", style = "directory") input
#@ File (label = "Output directory", style = "directory") outputDir
#@ String (label = "File suffix", value = ".tif") suffix
#@ String(label="What is your fluorescence channel order", description="Enter colors in order seperated by commas e.g. bf,green,red,far red,blue") channelOrder
// batch merge based on this format: r02c02-f01-Alexa 488-sk1fk1fl1
//Make sure your folder has no spaces - will get mad
macro "BatchMergeStacks_Montage"{
	channelColours = split(channelOrder,",");
	nChannels = lengthOf(channelColours);
	colour_rename(channelColours);
	function makeCoordinateString(row,col,field) { 
	// convert the integers into the Harmony RowColField syntax
		rowString = convertNumberTo2DigitString(row);
		colString = convertNumberTo2DigitString(col);
		fieldString = convertNumberTo2DigitString(field);
		rowcolfield = "r" + rowString + "c" + colString+"f"+ fieldString;
		return rowcolfield;
	}
	function convertNumberTo2DigitString(number) { 
	// convert a number to a two digit string, with a prefix 0 added to numbers below 10
		if (number < 10){ 
			number = "0" + number;
			}	
		return "" + number;
	}
	function makeRowColFieldString(imageName) { 
		// get the plate corrdinates based on this naming scheme Cell_9487_ch1_frame1_r01c24f01
		image_components=split(imageName, "_");
		rowcolfield = image_components[4];
		print(rowcolfield);
		return rowcolfield;
	}
	
	function openImage(input,imageName) { 
	// opens an image at specified rowcolfield 
		//add the extra slash to satisfy linux path
		//input_with_delimiter = input+ "/";
		
		//merge_ch(input_with_delimiter,rowcolfield,imageName,suffix,nChannels);
	}
	
	function colour_rename(channelColours){
		//rename colours to add flexibility

		for (i = 0; i < channelColours.length; i++) {
			colour = toLowerCase(channelColours[i]);
			if (colour == "g" || colour=="gfp" || colour=="488"){
					colour = "green";
			}
			else if (colour == "bf" || colour=="brightfield" || colour=="dic" || colour=="dpc"){
				colour = "bf";
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
			Array.print(channelColours);
			//return -1;
			exit("colour " + colour + " not found");
		}
		return colour_index
	}
	/*
	function getChannelsNames(channelColours) {
		//gfp_ch = "C" + chNames[get_colour_index("green")];
		channelsNames = newArray(5);
		channelsNames = Array.fill(channelsNames, "*None*");
		for (i = 0; i < lengthOf(channelColours); i++) {
			colour = channelColours[i];
			//1-index it
			channelsNames[i] = "C" + (channelColours[get_colour_index(colour)]+1);
		}
		return channelsNames;
	}
	channelsNames=getChannelsNames(channelColours);
	*/
	
	/*
	channel_ids = ["*None*","*None*","*None*","*None*"];
	ch_idx = 0;
	for (i = 0; i < 4; i++) {
		if(channelsNames[i] == "C-1"){
			channelsNames[i] = "*None*";
		}
		else{
			channel_ids[ch_idx] = channelsNames[i];
			ch_idx++;
		}
	}
	*/
	//sorted_channel_ids = Array.sort(channelsNames);
	function scanFolder(input) {

		list = getFileList(input);
		//list = Array.sort(list);
		increment=nChannels-1;
		setBatchMode("hide");
		for (i = 0; i < list.length; i++) {
			print(i);
			if(File.isDirectory(input + File.separator + list[i])){
				//recurse thru folders
				//print(list[i]);
				scanFolder(input + File.separator + list[i]);
			}
			Array.print(list);
			if(endsWith(list[i], suffix)) {
				imageName = list[i];
				//print(imageName+ i"/"+list.length/4);
				rowcolfield = makeRowColFieldString(imageName);
				path = input + File.separator + imageName;
				if(File.exists(path)){
					startIndex = 0;
					endIndex = nChannels;
					for (i = startIndex; i < endIndex; i++) {
			    		//open in order by channels
			    		open(path);
					}
				} else {
					exit("Error: File not found at location: " + path);
				}
				chNames = getList("image.titles");
				merge_ch(chNames,rowcolfield,suffix,nChannels);
				//openImage(input,imageName);
				i=i+increment;
				//processFile(input, output, list[i]);
			}
		}
	}
	function merge_ch(chNames,rowcolfield,suffix,channels) {
		//function to open each single-channel image from that location and merge into a color composite
		
		run("Merge Channels...", "red="+ chNames[get_colour_index("red")] +" green="+ chNames[get_colour_index("green")] +" gray="+ chNames[get_colour_index("bf")] +" magenta="+ chNames[get_colour_index("fr")] +" cyan="+ chNames[get_colour_index("blue")] +" create");
		for (i = 1; i <= nSlices; i++) {
			setSlice(i);
			if(i==1){
				//run("Green");
				run("Enhance Contrast", "saturated=0.35");
			}
			else if(i==2){
				//run("Grays");
				run("Enhance Contrast", "saturated=0.35");
			}
			else if(i==3){
				//run("Magenta");
				run("Enhance Contrast", "saturated=0.35");
			}
			else if(i==4){
				//run("Cyan");
				run("Enhance Contrast", "saturated=0.35");
			}
			else if(i==5){
				//run("Grays");
				run("Enhance Contrast", "saturated=0.35");
			}
			
		}
		//c3=blue, c4=gray, c5 = cyan, c6 = magenta
		selectImage("Composite");
		run("Make Montage");
		run("Make Montage...", "columns=5 rows=1 scale=1");
		//change image name to avoid confusion
		rename(rowcolfield+"_montage");
		rowcolfield_clean = replace(rowcolfield, "-", "");
		save(outputDir + "/" + rowcolfield_clean + suffix);
		close("*");
		
	}
	print(input);
	scanFolder(input);
	
	
}