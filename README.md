# Bunch Length Detector Data Collector Program
Program to collect BLD RF phase scan data. 

## Bugs & To-Do 
- also needs an alternative analysis path, esp if collecting data that turns out to be non-gaussian
- need to add the phase parameter update & default to the loadsetp 

- crashes if you try to change the phase parameter too much - it's crashing on the readbacks thread, but i can't figure out how to update the readbacks without killing that thread completely. we can try to click proof it by giving it time / a wait or something? but i think that's a janky fix. we can make the labelling more efficient but that still doesn't really help
- crashes if you upload a no bld then a no bld-no phase...
- another bug where the plotting won't work when you start, might abandon this branch


- check if the unlocking of entries releases the event combobox to a enabled, not a readonly state. event combobox should be readonly!!

# Completed
- add Setup Parameter Upload capability.
- gets hung up if you try to abort after collecting no data - fixed by adding a 1 Hz monitor of vacuum. this is probably a janky fix, but it's used in the WS one too...