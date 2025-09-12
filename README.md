# Bunch Length Detector Data Collector Program
Program to collect BLD RF phase scan data. 

## Bugs & To-Do 
- change it to not preallocate all arrays in the procdata outdictcollate because if you abort, there's a bunch of empty lists hovering around.
- lags if you try to switch BLDs too quickly...all I can say is slow down 

# Completed
- add Setup Parameter Upload capability.
- gets hung up if you try to abort after collecting no data - fixed by adding a 1 Hz monitor of vacuum. this is probably a janky fix, but it's used in the WS one too...
- add a pure scatter plot even if the analysis fails (fixed, along with other bugs involving the plotting-with-fit. mpl doesn't like printing text when one of the lines is a np.inf)
- also needs an alternative analysis path, esp if collecting data that turns out to be non-gaussian (not really sure what i meant by this, but there's a pure scatter if the analysis fails)
- bug sometimes the first time it's run no settings print ??? explain? - fixed, sometimes the count went too high which is because it was <= not <
- finish implementing setting into the gui side & the setting setup 
- FIX LIVEPLOTTING SCALING / PLOT!!! does not look like it's plotting right, but the saved png looks good (calibration data was in primary units of Volts, but we need to issue settings in Common units, so added a *2 globally.)
- save plot with errorbars in datanaalysis
- make sure calculations in dataanalysis are consistent with the settings issued in Volts, the readback a linear interpretation of phase, etc. esp. ps etc., if the RF is now 805 MHz scale, not 201 MHz. (changed the ps calcuation to be 1/805 not 1/201)
- bug where the first data point is just not right??? in terms of phase readback. (fixed this (moved dpm.start after the setting) and found a bigger bug that the time.sleep was delaying all the readings of the program. both bugs regarding data collection are fixed.)