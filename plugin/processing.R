# processing.R
# R script to be called from the main plugin Python file

# Python plugin passes data filename by means of storing a variable
imageData = read.csv(dataFilename)
