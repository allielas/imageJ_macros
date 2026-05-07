#@String directory

from ij import IJ
import os

im = IJ.open(os.path.join(directory, 'dummy.tiff'))
IJ.run("Invert")
im2 = IJ.getImage()
IJ.saveAs(im2,'tiff',os.path.join(directory,'inverseddummy.tiff'))
