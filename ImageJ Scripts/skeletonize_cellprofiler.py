#@ String directory
#@ OpService ops
from ij import IJ, Prefs
from ij import WindowManager as wm
from ij.gui import WaitForUserDialog, Roi, ShapeRoi, Toolbar
from ij.plugin import Duplicator
from ij.measure import ResultsTable
from ij.plugin.frame import RoiManager 
from ij.util import ThreadUtil

import os


#from ij.skeleton_analysis import AnalyzeSkeleton_,Graph,Edge,Vertex
# from the mina plugin
def ridge_detect(imp, rd_max, rd_min, rd_width, rd_length):
    title = imp.getTitle()
    IJ.run(imp, "8-bit", "");
    IJ.run(imp, "Ridge Detection", "line_width=%s high_contrast=%s low_contrast=%s make_binary method_for_overlap_resolution=NONE minimum_line_length=%s maximum=0" % (rd_width, rd_max, rd_min, rd_length))
    IJ.run(imp, "Remove Overlay", "")
    skel = wm.getImage(title + " Detected segments")
    IJ.run(skel, "Skeletonize (2D/3D)", "")
    skel.hide()
    return(skel)


def process_img(imp):
	#Preprocess

	IJ.run(imp, "Skeletonize (2D/3D)", "")
	imp = IJ.getImage()
	IJ.saveAs(imp,'tiff',os.path.join(directory,'skelmito.tiff'))
	#IJ.run(imp, "Analyze Skeleton (2D/3D)", "") #prune=[shortest branch] prune_0 calculate
	
	return imp
	#run_skel(imp)

# open image
#if using CP, assumes you are giving it a single-channel image
#if __name__ in ['__builtin__','__main__']:
imp=IJ.open(os.path.join(directory, 'dummy.tiff')) #note that dummy.tiff is the input image filename for cp, and "directory" is the directory variable
imp = IJ.getImage()
processed_img = process_img(imp)

ThreadUtil.threadPoolExecutor.shutdown()
	


