

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
checkPackage( c("ggplot2") )


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



attach(data)

variableX <- "XVARIABLE"
variableY <- "YVARIABLE"

detach(data)


#Scatterplot
scatterPlot <- function(xVar, yVar){
  library(ggplot2)
  plot <- qplot(xVar, yVar) + geom_smooth(method=lm,   # Add linear regression line
                                                                                        se=FALSE)
  ggsave(filename = paste("Test_ScatterPlot", curTime, ".jpg", sep=""), plot = plot)
}
with(data, scatterPlot(variableX, variableY))
