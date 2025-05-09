# Constant Speed Wire Scanner Program
Program to collect Linac wire scanner data using the fastest motor speed. 

## Bugs & To-Do 
- add LSTUDY enable/disable button and automatically start and stop L:STUDY upon a scan
- add a number of data points per position option
- add a number of scans option
- remove the upload button and have its functionalities be absorbed into the completion of "Browse"
- add example json to help page
- troubleshoot why D81, 83, E1, E3 don't work with acsys...
- fix that click focus hates combobox -- there's a pass right now to prevent the error
- lock access to dictionaries that are being accessed in multiple places [see Rich advice on Slack], specifically the set function
- clean up what's being passed between functions....
- handle duplicate Additional Parameters
- check what happens when you put in a bad configuration input
- incorporate alarm bypass
- coordinate log file
- change fig facecolor to the default color of the tkinter window...
- add units for additional readbacks
- maybe something to remind you that bstudy has dropped out

- consider adding in a big pause if beam stops??? intriguing...difficult to do based on position alone. consider using lstudy/bstudy digital status? 
- consider making the live plotting more efficient......not necessarily in the destruction/reconstruction of the object, but in the data reprocessing every time is tedious. 
- consider adding a warning that L:STUDY isn't enabled when you start the scan....also means frequency might be wrong


## Completed Tasks
- fix plotting spacing: separate the three subplots in the liveplot into three separate tk frames and three separate plots (or two, if it's the two-wire)
- fix csv/dict parsing when there's an empty list/no data? 
- abort / lockedentries deadlock - thank you Rich
- improve the protections on starting a new scan when one is existing -- add a finally event? i think it could be that you abort scan but something stalls on the finally statement and the new scan is given the go ahead even though the previous is unfinished because it's techincally set, but not joined. i agree that joining is not helpful here -- i must have lockentries accessed from the finally statement, and i cannot join from mainthread. fine. 
- assemble metadata collection & the requisite file (see notebook pg. 79): timestamp, folder, direction, event, user comment, source L:SOURCE, D7TOR, pulse length, frequency, (eventually) collimator status
- bug when you choose an event that isn't in the timeline at the moment...i think it can't break the acsys loop because it's not getting any events?? add a timer for finding event? - fixed by adding a periodic readback at tag -1...
- add messagebox message about scan completion
- add wires out button functionality, incorporate it into abort
- take out extra asynchio event loop [see Rich advice on Slack]
- save tagdict
- save reprocessed data from rawtowires in basicfuncs
- consider converting to unix time when gathering data vs. later
- fix rawtowires to ensure the timing is correct & that proccessed data are always the same length, with np.nan filling the gaps
- build basicfuncs.csvtodict
- add in default analysis of data and fitting etc. 
- add nan handler into the analysis -- needed boolean indexing and also conversion into numpy array
- fix matplotlib open figure in not main thread bug (when trying to make pngs to save)
- in some previous updated added a functionality to add abort = True etc. into the metadata by updating and rewriting the metadata file if this happens. this is stored in the abortbutton function
- fix bug for failing the kerberos authentication....puts up a ValueError. caught the value error both in initial validation for run scan and also in the abort. 
- fixed help page spacing


## Rejected Ideas
- consider locking the abort button until the scan starts...i don't think so 
- do we want a different thread working on analysis separate from the scan thread's finally? I don't really think so. i don't think there's a reason to start a "queue" of sorts for analysis. theoretically, analysis should be quick and it is fine to execute within the scope of the scan. if analysis is taking so long, there are other things that should be of concern and you really shouldn't initiate another scan. 
- locking access to the data: i understand why ralitsa does this in her code: read_many / set_many access to write to it, while get_thread_data actually clears the data. so there are two sources doing writing. but i would argue that only runscan accesses my data, and therefore there's no need to lock it. yes, when i read it, it is possible that it could be wonky from being simultaneously written. BUT consider that i don't really care about the quality of temporary data more than I care about the scan data collection being collected live & on schedule. i would prefer to prioritize the writing access to the data, because all of the readings are just temporary use cases. 