#@ File (style="directory") cropFolder
#@ File (style="directory") outputFolder
#@ String(label="What is your fluorescence channel order", description="Enter colors in order seperated by commas e.g. bf,green,red,far red,blue") channelOrder

macro "montage_folder from Quantixed" {
	//Macro to run the "Make Montage Directory" plugin from Quantixed
	//Make sure your folder has no spaces - will get mad
	channelColours = split(channelOrder,",");
	nChannels = lengthOf(channelColours);
	colour_rename(channelColours);
	
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
	
	function colour_rename(channelColours){
		//rename colours to add flexibility

		for (i = 0; i < channelColours.length; i++) {
			colour = toLowerCase(channelColours[i]);
			if (colour == "g" || colour=="gfp" || colour=="488"){
					colour = "green";
			}
			else if (colour == "bf" || colour=="brightfield" || colour=="dic" || colour=="gray"){
				colour = "gray";
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
	
	red_ch = channelsNames[get_colour_index("red")];
	gfp_ch = channelsNames[get_colour_index("green")];
	fr_ch = channelsNames[get_colour_index("fr")];
	DAPI_ch = channelsNames[get_colour_index("blue")];
	bf_ch = channelsNames[get_colour_index("gray")];
	Array.print(channelsNames);
	scale = 10;
	run("Make Montage Directory", "source="+ cropFolder+" destination="+outputFolder+" gray="+nChannels+" merge=1 g1="+channelsNames[0]+" g2="+channelsNames[1]+"g3="+channelsNames[2]+" g4="+channelsNames[3]+" g5="+channelsNames[4]+" red="+red_ch+" green="+gfp_ch+" blue=*None* gray="+bf_ch+" cyan="+DAPI_ch+" magenta="+fr_ch+" yellow=*None* grout=8 dpi=300 include scale="+scale+" scaling,1=0.069");
	
}