# Bunch Length Detector Data Collector Program
Program to collect BLD RF phase scan data. 

## Bugs & To-Do 
- also needs an alternative analysis path, esp if collecting data that turns out to be non-gaussian
- add a pure scatter plot even if the analysis fails
    - there's something about the specific line of text in the textstr that causes the thread to fail, even though it's inside a try/except. 
      using dummy text means there's no issue. 
    

# Completed
- add Setup Parameter Upload capability.
- gets hung up if you try to abort after collecting no data - fixed by adding a 1 Hz monitor of vacuum. this is probably a janky fix, but it's used in the WS one too...