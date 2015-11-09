# Image Processing in Fiji
Project for John Carroll University CS470 Fall 2015

## Purpose
The goal of the software is to perform post-processing and statistical analysis on a set of images. Any number of images can be opened and sent through an arbitrary pipeline of processes. After processing, the results will be passed on to statistical software that will provide a final output from the images. 

## Installation Instructions
1. **Install the Prerequisites:**
	* Fiji (Fiji Is Just ImageJ)
		* [Download here](http://fiji.sc/Downloads#Fiji)
		* Requires [Java](http://www.oracle.com/technetwork/java/javase/downloads/jre8-downloads-2133155.html)
		* After installation, run the updater and install updates when prompted.
	* R
		* Required for statistical analysis
		* To download, click [here](https://cran.r-project.org/mirrors.html) and select a mirror site.
2. **Get the Code:** Either clone the repository, or download the plugin folder.
3. **Install Plugin File:** From Fiji's `Plugins` menu, select `Install PlugIn...`, and select `Medical_Image_Processing.py`.

## Usage Instructions
### Macros
This plugin allows a user to define Fiji macros (`.ijm` files) and generalizes them to apply to a large collection of files. A sample macro file is included.
### R Script
The plugin asks for an R script to be run after processing images. A template R script is included to demonstrate how to open the resulting data. A sample R script is also included. 

## Other Notes
### Final .zip File
The final product will be delivered as a .zip file that will contain:
* The main plugin file `Medical_Image_Processing.py`
* A sample macro file
* A sample R script
* An R template that the user can use to make custom R scripts

