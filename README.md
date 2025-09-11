# Bunch Length Detector Data Collector Program
Program to collect BLD RF phase scan data. 

## Bugs & To-Do 
- make sure calculations in dataanalysis are consistent with the settings issued in Volts, the readback a linear interpretation of phase, etc. esp. ps etc., if the RF is now 805 MHz scale, not 201 MHz.
- does still lag if you try to switch BLDs too quickly...all I can say is slow down 
- finish implementing setting into the gui side & the setting setup 

# Completed
- add Setup Parameter Upload capability.
- gets hung up if you try to abort after collecting no data - fixed by adding a 1 Hz monitor of vacuum. this is probably a janky fix, but it's used in the WS one too...
- add a pure scatter plot even if the analysis fails (fixed, along with other bugs involving the plotting-with-fit. mpl doesn't like printing text when one of the lines is a np.inf)
- also needs an alternative analysis path, esp if collecting data that turns out to be non-gaussian (not really sure what i meant by this, but there's a pure scatter if the analysis fails)