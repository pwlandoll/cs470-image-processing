# Template R Script
# Use this script to create custom R scripts
# The call to checkPackage at the end can be changed to install a custom list of package

#Clear global enviornment
rm(list = ls(all.names = TRUE))

#Libraries should now install to /Users/"you"/R/win-library/x.y, 
#for which you have the appropriate permissions.
dir.create(Sys.getenv("R_LIBS_USER"), recursive = TRUE)

# Retrieve Date and Time
# Date will be used to create a new directory
# Time will be used to save files into that new directory. (Timestamp)
curDate <- Sys.Date()
curDate_Time <- Sys.time()
curTime <- format(Sys.time(), "%I_%M %p")

# Function to install packages if not installed.
# If you create a method that requires a different package along with the ones listed below, 
#simply add a comma followed by "your package name", after "plyr" below.It will automatically test if it 
#is installed and if not will install it.
#This will keep r from restarting everytime the package is already installed.
checkPackage <- function(x){
  for( i in x ){
    #  require returns TRUE invisibly if it was able to load package
    if( ! require( i , character.only = TRUE ) ){
      #  If package was not able to be loaded then re-install
      install.packages( i , dependencies = TRUE )
    }
  }
}
# Try/install packages...Insert any more packages that may be needed here
checkPackage( c("methods", "ggplot2") )

outputDirectory <- commandArgs(trailingOnly = TRUE)[1]

# This is the code to read all csv files into R.
# Create One data frame.
path <- paste0(outputDirectory, "/", sep="")
print(path)
file_list <- list.files(path = path, pattern="*.csv")
data <- do.call("rbind", lapply(file_list, function(x) 
  read.csv(paste(path, x, sep = ""), stringsAsFactors = FALSE)))

# Create a subdirectory based on the curDate variable for saving plots.
# A Folder is created with the current date as it's name
dir.create(file.path(path,curDate), showWarnings = FALSE)
# Set newly created folder as working directory. Now all files saved will be
# saved into that location
setwd(paste(path,curDate,"/",sep = ""))

#Create a new data frame based on if the word area is found in any of the columns
#If this is the case, a new data frame will be created based on those area columns
#This can similarily be done with other variables. Simply substitue area with a new word/subset of letters.
areaCol <- data[grep("area", names(data), value = TRUE,ignore.case = TRUE)]
sink(file=paste0("Area Summary_",curTime, ".txt", sep = "")) 
summary(areaCol)
sink(NULL)

#Check if initial data frame is null. If that is the case the lines below will not run.
# This function should return a proper list with all the data.frames as elements.
dfs <- Filter(function(x) is(x, "data.frame"), mget(ls()))
dfNames <- names(dfs)
for(x in 1: length(dfs)){
  df.name <- dfNames[x]
  print(df.name)
  colnames(dfs[[x]])[1]
  # Has a new column created specifying which data frame it is from (labeling purposes)
  dfs[[x]]$fromDF <- df.name
}

#Create a text file summarizing the data from all the csv files
sink(file=paste0("Complete Data Summary_",curTime, ".txt", sep = "")) 
summary(data)
sink(NULL)

# Return each unique variable from Base.Image Column. (No Repeats)
count <- unique(data$Base.Image)
# Return the count of the number of rows in the previous variable count
count <- length(count)
# Create a color palette with the amount return from count.
# R palette is only set to 8 different colors to begin with
col.rainbow <- rainbow(count)
# Set current palette to col.rainbow created above
palette(col.rainbow)

#Plot All indexes for One Variable at a time.
for ( i in seq(1,length( data ),1) ){
  #Plotting numerical data. Will only look for variables that are either integer or double
  if(typeof(data[[i]]) == "integer" | typeof(data[[i]]) == "double"){
  jpeg(paste("Numerical Plot ",names(data[i]),"  ", curTime, ".jpg", sep=""), width = 1500, height = 900)
  # Type B will output both points and lines.Base.Image must be included from FIJI Macro.
  # Plots index of image vs. Variable Column. *Columns are not compared against one another
  plot(data[,i],ylab=names(data[i]), type = "b", col = factor(data$Base.Image))
  #Need legend. Scalibility issue.
  dev.off()
  }
}

#Plotting two variables passed in: Scatterplot
variableX<- Pass variable here.
variableY<- Pass variable here.
library(ggplot2)
#If both variables are of numberic type...
if(isTRUE(typeof(varaibleX == "integer" | typeof(variableX) == "double") &
  isTRUE(typeof(variableY) == "integer" | typeof(variableY) == "double")))
{
#Create a scatterplot with a regression line
plot <- qplot(variablex, variabley)+ geom_smooth(method=lm,se=FALSE)
ggsave(filename = paste("Test_ScatterPlot", curTime, ".jpg", sep=""), plot = plot)
}
