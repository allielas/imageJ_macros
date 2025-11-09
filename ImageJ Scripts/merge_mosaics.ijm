macro "OpenMaxProjMosaic_Phenix"{
#@ File (label = "Input directory", style = "directory") input
#@ File (label = "Output directory", style = "directory") outputDir
#@ String (label = "File suffix", value = ".tif") suffix
#@ int (value=1, min=1, max=16, style="slider") row 
#@ int (value=1, min=1, max=24, style="slider") col 
#@ String (label = "A or B", value = "A") field_block


	//add the extra slash to satisfy linux path
	input = input+ "/";
	nChannels = 4;
	//print(nChannels);
	openImage(input,suffix);
	
	function makeCoordinateString(row,col) { 
	// convert the integers into the Harmony RowColField syntax
		rowString = convertNumberTo2DigitString(row);
		colString = convertNumberTo2DigitString(col);

		rowcolfield = "r" + rowString + "c" + colString;
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
		rowcolfield = makeCoordinateString(row,col);
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
	
	function get_colour(colour_index){
		//define colours based on your image channels, returns the index of your colour value
		colours=newArray("Alexa 488","Alexa 568", "Alexa 647", "DAPI");
		
		if(colour_index==-1)
		{
			//Array.print(channelColours);
			exit("colour " + colour + " not found");
		}
		else{
			colour=colours[colour_index];
		}
		return colour;
	}
	function merge_ch(path,rowcolfield,suffix,channels) {
		//function to open each single-channel image from that location and merge into a color composite
		close("*");
		base_filename = rowcolfield +"--" + "Alexa 488" + "-sk1fk1fl1_" + field_block + suffix; //construct base file name based on phenix format
		
		if(File.exists(path + base_filename)){
			startIndex = 0;
			endIndex = channels;
			for (i = startIndex; i < endIndex; i++) {
	    		//open in order by channels
	    		colour = get_colour(i);
				curr_img_path = path + rowcolfield +"--" + colour + "-sk1fk1fl1_" + field_block + suffix;
	    		open(curr_img_path);
			}
			chNames = getList("image.titles"); //get the 0-indexed list
			//Array.print(chNames);
			//define colour channels mappings as ch -1 
			if(nChannels ==3) {
				//run("Merge Channels...", "red="+ chNames[get_colour_index("red")] +" green="+ chNames[get_colour_index("green")] +" c5="+ chNames[get_colour_index("blue")] +" create");
			}
			else {
				run("Merge Channels...", "c1=[" + chNames[0] +"] c2=["+ chNames[1] +"] c3=["+ chNames[2] + "] c4=[" + chNames[3] +"] create");
			}//Make sure to have the square brackets
			for (i = 1; i <= nChannels; i++) {
				setSlice(i);
				if(i==1){
					run("Green");
					setMinAndMax(250, 6000);
				}
				else if(i==2){
					run("Grays");
					setMinAndMax(250, 4000);
				}
				else if(i==3){
					run("Magenta");
					run("Enhance Contrast", "saturated=0.35");
				}
				else if(i==4){
					run("Cyan");
					run("Enhance Contrast", "saturated=0.35");
				}
			}
			//c3=blue, c4=gray, c5 = cyan, c6 = magenta
			
			//change image name to avoid confusion
			rename(rowcolfield);
			save(outputDir + "/" + rowcolfield +"_" + field_block + suffix);
		} else {
			exit("Error: File not found at the plate coordinates: " + rowcolfield + "\nin directory: \n" + path);
		}
	}
}
