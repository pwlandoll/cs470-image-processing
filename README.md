# MIPPy - Medical Image Processing in Python
Project for John Carroll University CS470 Fall 2015

## Purpose
The goal of the software is to perform post-processing and statistical analysis on a set of images through the Fiji platform. The plugin allows any number of images to be opened and sent through an arbitrary pipeline of processes. After processing, the results will be passed on to statistical software that will provide a final analysis from the image input. 

## Installation Instructions
1. **Install the Prerequisites:**
	* Fiji (Fiji Is Just ImageJ)
		* [Download here](http://fiji.sc/Downloads#Fiji)
		* Requires [Java](http://www.oracle.com/technetwork/java/javase/downloads/jre8-downloads-2133155.html)
		* After installing Fiji, update to the latest version by opening the ‘Help’ menu and selecting ‘Update ImageJ…’
		* NOTE: Reading the documentation and instructions on Fiji’s website is recommended 
	* R
		* Required for statistical analysis
		* To download, click [here](https://cran.r-project.org/mirrors.html) and select a mirror site.
		* IMPORTANT: Windows users should take note of where R is installed
2. **Download the Software:** To install the plugin, download the [Medical_Image.zip file](https://github.com/pwlandoll/cs470-image-processing/raw/master/Medical_Image.zip) and extract to the ‘plugins’ folder in Fiji. 
	* Windows/Linux
		1. Extract the zip file to the ‘plugins’ folder of the Fiji.app folder downloaded earlier. If there is an option to create a new folder for the extracted files, do not select it.
		2. Restart Fiji
	* OS X
		1. Double-click/extract the zip file
		2. Open a Finder window, and from the ‘Go’ menu, select ‘Go to Folder’
		3. In the text field, type ‘/Applications/Fiji.app/plugins’
		4. Drag the extracted folder into the open plugins folder
		5. Restart Fiji

For more information on installation, usage, and troubleshooting, see `MIPPyUserGuide.pdf`. 

## Medical_Image.zip File
The software is delivered as a .zip file that will contain:
* The main plugin file `Medical_Image_Processing.py`
* Another Python file, `View_Step.py`
* A sample macro file
* A sample R script
* A basic R script with functionality to compare variables
* An R template that the user can use to make custom R scripts
* A copy of the User Guide

