

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
checkPackage( c("ggplot2", "car") )


# This is the code to read all csv files into R.
# Create One data frame.
path <- paste0(getwd(), "/")
file_list <- list.files(path = path, pattern="*.csv")
data <- do.call("rbind", lapply(file_list, function(x) 
  read.csv(paste(path, x, sep = ""), stringsAsFactors = FALSE)))


sink(file=paste0("Complete Data Summary_",curTime, ".txt", sep = "")) 
summary(data)
sink(NULL)

#Create a new data frame based on if the word area is one of the header
areaCol <- data[grep("area", names(data), value = TRUE,ignore.case = TRUE)]
sink(file=paste0("Area Summary_",curTime, ".txt", sep = "")) 
summary(areaCol)
sink(NULL)

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

#Scatterplot
scatterPlot <- function(xVar, yVar){
  library(ggplot2)
  plot <- qplot(xVar, yVar) + geom_smooth(method=lm,   # Add linear regression line
                                                                                        se=FALSE)
  ggsave(filename = paste("Test_ScatterPlot", curTime, ".jpg", sep=""), plot = plot)
}
with(data, scatterPlot(variableX, variableY))


scatterplotMatrix<- function(){
  jpeg(paste("Merged Data Matrices", curTime, ".jpg", sep=""), width = 850)
  library(car)
  scatterplot.matrix(~variableX+variableY|Base.Image, data = data)
  dev.off()
}
scatterplotMatrix()
