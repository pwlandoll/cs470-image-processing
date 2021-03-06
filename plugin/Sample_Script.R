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

#  Then try/install packages...Insert any more packages that may be needed here
checkPackage( c("ggplot2","psych","corrgram", "plyr", "car", "reshape2", "vcd", "hexbin") )

outputDirectory <- commandArgs(trailingOnly = TRUE)[1]

# This is the code to read all csv files into R.
# Create One data frame.
path <- paste0(outputDirectory, "/", sep="")
print(path)
file_list <- list.files(path = path, pattern="*.csv")
data <- do.call("rbind", lapply(file_list, function(x) 
  read.csv(paste(path, x, sep = ""), stringsAsFactors = FALSE)))

#Add a column specifying ct or xray
data$Image.Type <- ""

#Create data frames based on CT in the Image.Name variable
CT_Data <-data[grep("ct", data$Image.Name,  ignore.case = TRUE),]
#Change row in Image Type to CT
CT_Data$Image.Type = "CT"

#Create data frames based on XRAY in the Image.Name variable
XRay_Data <- data[grep("xr", data$Image.Name,  ignore.case = TRUE),]
#Change row in Image Type to XRAY
#nonCT_XRay <- data[grep("xr|ct", data$Image.Name, ignore.case = TRUE, invert = TRUE),]
XRay_Data$Image.Type = "XRAY"

#Merge two tables into new data frame
data_merge <- rbind(CT_Data, XRay_Data)

#Remove Image.Type column from data frame to retain original data
data$Image.Type = NULL

# Create a subdirectory based on the curDate variable for saving plots.
# (If today is 4/4/14, then a new folder will be created with that date and any work done on that day will be 
# saved into that folder.)Will then set current directory to the new direcory created. 
# This way all the data has already been loaded into the global enviornment per the previous directory. 
# Now all new plots will be saved to the new directory.
dir.create(file.path(path,curDate), showWarnings = FALSE)
setwd(paste(path,curDate,"/",sep = ""))



# This function should return a proper list with all the data.frames as elements.
# Has a new column added specifying which data frame it is from (labeling purposes)
dfs <- Filter(function(x) is(x, "data.frame"), mget(ls()))
dfNames <- names(dfs)
for(x in 1: length(dfs)){
  df.name <- dfNames[x]
  print(df.name)
  colnames(dfs[[x]])[1]
  dfs[[x]]$fromDF <- df.name
}

# Kernel density plots 
# grouped by CT and XRay
densityPlot<- function(dataFrame, Variable, VariableLabel, Fill){
  library(ggplot2)
  plot <- qplot(Variable, data=dataFrame, geom="density", fill=Fill, alpha=I(.5),
        xlab = VariableLabel)
  ggsave(filename = paste0(VariableLabel, "_DensityPlot", curTime, ".jpg", sep = ""), plot = plot)
}
with(data_merge, densityPlot(data_merge,StdDev, "StdDev", Image.Type))
with(data_merge, densityPlot(data_merge,Skew, "Skew", Image.Type))
with(data_merge, densityPlot(data_merge,X.Area,"X.Area", Image.Type))

#Scatterplot
scatterPlot <- function(label,xVar, xString, yVar, yString){
  library(ggplot2)
  #Will specify CT or XRay
  label_1 <- label[[1]]
  plot <- qplot(xVar, yVar, xlab = xString, ylab = yString, main = label) + geom_smooth(method=lm,   # Add linear regression line
                                                                                      se=FALSE)
  ggsave(filename = paste(label_1,"_", xString, " vs ", yString, "_ScatterPlot", curTime, ".jpg", sep=""), plot = plot)
}
with(CT_Data, scatterPlot(Image.Type,StdDev, "StdDev", Mean, "Mean"))
with(XRay_Data, scatterPlot(Image.Type,StdDev, "StdDev", Mean, "Mean"))

#Regression
regressionPlot <- function(fillVar, xVar, xLabel, yVar, yLabel){
  library(ggplot2)
  plot <- qplot(xVar, yVar,geom=c("point", "smooth"), 
        method="lm", formula=y~x, color=fillVar, main = "Regression Plot")
 ggsave(filename = paste0(xLabel," vs ", yLabel, "_Regression", curTime, ".jpg", sep = ""), plot = plot)
}

with(data_merge, regressionPlot(Image.Type,StdDev, "StdDev", Mean, "Mean"))

# Boxplot
# observations (points) are overlayed and jittered
boxPlot <- function(xVar, xLabel, yVar, yLabel){
  library(ggplot2)
  plot <- qplot(xVar, yVar,geom=c("boxplot", "jitter"), 
        fill=xVar, ylab = yLabel, xlab = "", main = xLabel)
  ggsave(filename = paste0(xLabel, " vs ", yLabel, "_BoxPlot", curTime, ".jpg", sep = ""), plot = plot)
}
  with(data_merge, boxPlot(Image.Type, "Image Type", StdDev, "StdDev"))
  with(data_merge, boxPlot(Image.Type, "Image Type", StdDev, "Mean"))
 
scatterplotMatrix<- function(){
  jpeg(paste("Merged Data Matrices", curTime, ".jpg", sep=""), width = 850)
  library(car)
  scatterplot.matrix(~Area+Mean+StdDev+X.Area|Image.Type, data = data_merge)
  dev.off()
}
scatterplotMatrix()

sink(file=paste0("Complete Data Summary_",curTime, ".txt", sep = "")) 
summary(data_merge)
sink(NULL)

#Create a new data frame based on if the word area is found in any of the columns
#If this is the case, a new data frame will be created based on those area columns
areaCol <- data[grep("area", names(data), value = TRUE,ignore.case = TRUE)]
sink(file=paste0("Area Summary_",curTime, ".txt", sep = "")) 
summary(areaCol)
sink(NULL)
