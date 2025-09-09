# Bunch Length Detector Data Collector Program
Program to collect BLD RF phase scan data. 

## Bugs & To-Do 
- also needs an alternative analysis path, esp if collecting data that turns out to be non-gaussian
- does still lag if you try to switch BLDs too quickly...all I can say is slow down 
    

# Completed
- add Setup Parameter Upload capability.
- gets hung up if you try to abort after collecting no data - fixed by adding a 1 Hz monitor of vacuum. this is probably a janky fix, but it's used in the WS one too...
- add a pure scatter plot even if the analysis fails (fixed, along with other bugs involving the plotting-with-fit. mpl doesn't like printing text when one of the lines is a np.inf)