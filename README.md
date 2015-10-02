# Image Processing in Fiji
Project for John Carroll University CS470

## Purpose
The goal of the software is to perform post-processing and statistical analysis on a set of images. Any number of images can be opened and sent through an arbitrary pipeline of processes. After processing, the results will be passed on to statistical software that will provide a final output from the images. 

## Prerequisites
1. Fiji (Fiji Is Just ImageJ)
	* [Download here](http://fiji.sc/Downloads#Fiji)
	* Requires Java
2. R
	* Required for statistical analysis
	* To download, click [here](https://cran.r-project.org/mirrors.html) and select a mirror site.
3. PypeR
	* Required for running R commands
	* NOTE: Windows requires R to be added to the PATH; `C:\Program Files\R\R-X.X.X\bin\x64` for 64-bit systems, `C:\Program Files\R\R-X.X.X\bin\i386` for 32-bit.
	* Install using `pip install pyper` from the command line
	* Project website [here](http://www.webarray.org/softwares/PypeR/)
	* Some instructions [here](http://www.jstatsoft.org/article/view/v035c02/v35c02.pdf)

## Installation Instructions
1. **Get the Code:** Either clone the repository, or download the plugin folder.
2. **Install Plugin Files:** From Fiji's `Plugins` menu, select `Install...`, and select `Medical_Image_Processing.py`.
	* Optional: Create a folder for the plugin
