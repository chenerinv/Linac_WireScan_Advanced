Notes on the program: 

- The devicesave module is a lighter, AcSys Python based alternative to the Java Linac Device Save. It collects data on the specified event or periodicity from the given devices for a time-based duration. It will collect both reading and setting information, when applicable.
- Beam must be enabled before the program is run. 
- Currently there is no "number of readings" based counter or a description of how many readings contributed to the average and standard deviation recorded. These functionalities can be added on request. 

Files in the ZIP: 
- test.py is an example of how to call the program & the inputs you need to provide. 
	devices can be a text file with the format shown in "devicelist.txt" or it can be a list of parameter strings
	event should be a string that is appended after the @ in the AcSys format. It can be event or periodic.
	timer is a int or float that specifies how long data collection should last for in seconds.
	savepath is a string path and/or name for the saved file. 
- devicelist.txt is an example of a text file input for a list of parameters to record. You do not need to specify different parameters for reading and setting; if available, setting will be automatically recorded. 
- devicesave.py contain the class that should be imported. 

Updated 22 April 2025. 


7/3/2025: Added event name to the filename and added number of points collected to the output data. 

Notes on improvements: 
Ideally we'd like to wait until a maximum time limit to collect a fixed number of points for each device. 
But this is complicated by the fact that we allow specification of devices without saying if they are reading, setting, or both. 
This means we get a lot of empty slots which we've taken advantage of. 
But it is very prohibitive to counting the number of events per device, because some devices will stay 0 because they don't exist.
One way we could get around it is by specifying if it's R, S, or both in the supplied devices. 

Another complication is that you might want to log some things on event but some things periodically...what to do!

