open("FILEPATH");
run("FFT");
run("Bio-Formats Exporter", "save=[FILEPATH\\IMAGENAME]");
close();
run("Measure");
saveAs("Results", "FILEPATH\\RESULTS.csv");
selectWindow("389266.jpg");
close();
