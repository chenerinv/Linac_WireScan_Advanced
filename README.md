# Bunch Length Detector Data Collector Program
Program to collect BLD RF phase scan data. 

## Bugs & To-Do 
- also needs an alternative analysis path, esp if collecting data that turns out to be non-gaussian
- need to add the phase parameter update & default to the loadsetp 
- crashes if you try to change the phase parameter too much - i tried to mitigate this by only realoading the axis part of the object, not initializing the whole plot, but it's still exceedingly inefficient.
- check if the unlocking of entries releases the event combobox to a enabled, not a readonly state. event combobox should be readonly!!

# Completed
- add Setup Parameter Upload capability.
- gets hung up if you try to abort after collecting no data - fixed by adding a 1 Hz monitor of vacuum. this is probably a janky fix, but it's used in the WS one too...