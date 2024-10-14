import threading
import acsys.dpm
import os
import basicdata
import basicfuncs
import time
from dataanalysis import dataanalysis

async def updatereadback_1H(con,threadcontext,strvardict):
    """Retrieve data for live readbacks."""
    # setup context
    async with acsys.dpm.DPMContext(con,dpm_node="DPM03") as dpm:
        # add acquisition requests
        tagdict = {}
        i = 0
        for key in list(strvardict.keys()):
            await dpm.add_entry(i,key+"@p,1H")
            tagdict[i]=key
            i=i+1
        # start acquisition
        await dpm.start()
        # process incoming data. setting 'stop' is exit condition
        async for evt_res in dpm:
            if threadcontext['stop'].is_set(): 
                break
            if evt_res.isReading: 
                # logic to assign 
                strvardict[tagdict[evt_res.tag]].set(round(evt_res.data,2))
            else: 
                pass  

async def runscan(con,threadcontext,maindict,messageprint): 
    """Run a scan."""
    # setup context
    async with acsys.dpm.DPMContext(con,dpm_node="DPM03") as dpm:
        # configure setting:
        # check kerberos credentials and enable settings
        try: 
            await dpm.enable_settings(role='linac_wirescan') #TODO UNCOMMENT WHEN ALLOWED TO MOVE WS!!!
        except: 
            messageprint("Invalid Kerberos realm.\n")  #TODO change to messageprint
            return
        # add acquisition requests
        await dpm.add_entry(-1,'G:AMANDA@p,1H') # this is to let us check set even without an event
        await dpm.add_entry(0, 'L:'+maindict['Wire']+'WPX.SETTING@N')  

        # add acquisition requests
        for key in maindict['Tags'].keys():
            await dpm.add_entry(key,maindict['Tags'][key]+"@e,"+maindict['Event'])
        
        # issue appropriate setting 
        if maindict["Direction"] == 1: steps = maindict["Steps"]*-1
        elif maindict["Direction"] == 0: steps = maindict["Steps"]
        await dpm.apply_settings([(0, steps)]) # set value  #TODO UNCOMMENT WHEN ALLOWED TO MOVE WS!!!
        g = 0

        # start acquisition
        await dpm.start()

        # process incoming data. setting 'stop' is exit condition
        async for evt_res in dpm:
            if threadcontext['stop'].is_set(): 
                break
            if evt_res.isReading: 
                # skip the setting & 1H setting and save data for all other tags
                if (evt_res.isReadingFor(0) is False) and (evt_res.isReadingFor(-1) is False): 
                    if evt_res.isReadingFor(1): # check the position
                        if maindict["Direction"] == 0: 
                            if evt_res.data > maindict["In Limit"]: 
                                threadcontext['stop'].set()
                        elif maindict["Direction"] == 1: 
                            if evt_res.data < maindict["Out Limit"]: 
                                threadcontext['stop'].set()
                    threadcontext['outdict']['tags'].append(evt_res.tag)
                    threadcontext['outdict']['data'].append(evt_res.data)
                    threadcontext['outdict']['stamps'].append(evt_res.stamp.timestamp())

                    g=g+1 # TODO COMMENT SECTION WHEN ALLOWED TO MOVE WS
                    # if g > 1000: 
                    #     threadcontext['stop'].set()
                    #     print("threadstopped in temporary counter!")            
            else: 
                pass # this is likely a status response

async def checkp(con,paramstrs,result,tries):
    """Check a parameter value."""
    # setup context
    async with acsys.dpm.DPMContext(con,dpm_node="DPM03") as dpm:
        # add acquisition requests
        for i, paramstr in enumerate(paramstrs): 
            await dpm.add_entry(i,paramstr) 

        # start acquisition
        await dpm.start()
        count1 = 0

        # process incoming data. Need better exit condition.
        async for it_res in dpm:
            if count1 < tries: 
                if it_res.isReading:
                    result['value'][it_res.tag] = it_res.data
                    if False not in result['value']: 
                        break
                else:
                    count1 = count1+1
                    pass # this is likely a status response
            else:
                break # it failed to get the data in the number of specified tries
    return result['value']

async def setp(con,paramstr,setting): 
    """Set a parameter to a value."""
    # setup context
    async with acsys.dpm.DPMContext(con,dpm_node="DPM03") as dpm:
        # check kerberos credentials and enable settings
        if paramstr[0] == "L":
            await dpm.enable_settings(role='linac_wirescan') 
        else: 
            await dpm.enable_settings(role='testing') 
        await dpm.add_entry(0, paramstr+'.SETTING@N')
        await dpm.apply_settings([(0, setting)]) 

class acsyscontrol: 
    def __init__(self): 
        self.thread_dict = {}
        self.dataanalysis = dataanalysis()

# starting threads and thread management: 
    def get_list_of_threads(self): 
        """Returns list of unset threads."""
        return [key for key in self.thread_dict.keys() if not self.thread_dict[key]['stop'].is_set()] 
    
    def check_finally(self,thread_dict_key): 
        """Checks if a thread has finished its finally statement and set the end of the finally."""
        if thread_dict_key in self.thread_dict.keys(): 
            if self.thread_dict[thread_dict_key]['finally'].is_set(): 
                return True
            else: 
                return False
        else: 
            return True
    
    def end_any_thread(self, thread_name): 
        """Ending a thread. Joins threads except mainscan."""
        self.thread_dict[thread_name]['stop'].set() 
        if thread_name != "mainscan":
            self.thread_dict[thread_name]['thread'].join() 

    def start_readbacks_thread(self, thread_name, strvardict): 
        """Start readbacks thread to gather data for readbackpopup and addparampopup"""
        tread = threading.Thread(target=self.readparams,args=(thread_name,strvardict,),daemon=True)
        self.thread_dict[thread_name] = {
            'thread': tread,
            'stop': threading.Event()
        }
        tread.start()

    def start_scan_thread(self,thread_name,coutput,lockentries,messageprint,plot_thread_name): 
        """Start mainscan thread."""
        tmscan = threading.Thread(target=self.mainscan,args=(thread_name,coutput,lockentries,messageprint,plot_thread_name,))
        self.thread_dict[thread_name] = {
            'thread': tmscan, 
            'finally': threading.Event(),
            #'lock': threading.Lock(),
            'stop': threading.Event(),
            'outdict': {'tags': [], 'data': [],'stamps': []}
        }
        tmscan.start()

    def start_liveplot_thread(self,thread_name,scanthreadname,modstr,plotobjects):
        """Start liveplot thread."""
        tplot = threading.Thread(target=self.liveplotting,args=(thread_name,scanthreadname,modstr,plotobjects,),daemon=True) 
        self.thread_dict[thread_name] = {
            'thread': tplot,
            'stop': threading.Event()
        }
        tplot.start()

# functions to happen inside of threads:
    def setparam(self,paramstr,setting): 
        """Set a parameter to a provided value."""
        acsys.run_client(setp,paramstr=paramstr,setting=setting)

    def checkparam(self,paramstrs,tries): 
        """Check the value of a parameter or list of parameters."""
        result = {'value': []}
        for j in paramstrs: 
            result['value'].append(False)
        output = acsys.run_client(checkp,paramstrs=paramstrs,result=result,tries=tries)
        return output
         
    def readparams(self,thread_name,strvardict): 
        """Continuously gather data for readbacks."""
        try: 
            acsys.run_client(updatereadback_1H,threadcontext=self.thread_dict[thread_name],strvardict=strvardict)             
        finally: 
            self.thread_dict[thread_name]['stop'].set()

    def mainscan(self,thread_name,coutput,lockentries,messageprint,plot_thread_name): 
        """Execute mainscan."""
        try: 
            acsys.run_client(runscan,threadcontext=self.thread_dict[thread_name],maindict=coutput,messageprint=messageprint)             
        finally: 
            # save data in threaddict to csv raw
            basicfuncs.dicttocsv(self.thread_dict[thread_name]['outdict'],os.path.join(coutput["WS Directory"],"_".join([str(coutput["Timestamp"]),coutput["Wire"],"RawData.csv"])))
            # end live plotting
            if plot_thread_name in self.get_list_of_threads(): 
                self.thread_dict[plot_thread_name]['stop'].set()
            # unlock entries
            lockentries("enabled",basicdata.lockedentries,basicdata.lockedbuttons) 
            # process data
            procdata = basicfuncs.rawtowires(self.thread_dict[thread_name]['outdict'],coutput["Wire"])
            basicfuncs.dicttocsv(procdata,os.path.join(coutput["WS Directory"],"_".join([str(coutput["Timestamp"]),coutput["Wire"],"ProcData.csv"])))
            # analyze data
            if self.thread_dict[thread_name]['outdict']['tags'] != []: # skip analysis if the dict is empty
                self.dataanalysis.endscanproc(procdata,coutput)
            # thread done, can be closed
            self.thread_dict[thread_name]['finally'].set()
            messageprint("Scan closed.\n")

    def liveplotting(self,thread_name,scanthreadname,modstr,plotobjects): 
        """Control for updating the plot."""
        try: 
            while self.thread_dict[thread_name]['stop'].is_set() is False: 
                try: 
                    self.animateplot(scanthreadname,modstr,plotobjects)
                    time.sleep(0.5) # 2 Hz plot update time
                except ValueError: 
                    print("Value Error")
                    pass # TODO probably need to address this truly
        finally: 
            print("Closing live plotting naturally.")
            self.thread_dict[thread_name]['stop'].set()
    
    def animateplot(self,scanthreadname,modstr,plotobjects): 
        """Update the plot once."""
        # plotobjects = {"Frame":{},"Canvas":{},"Fig":{},"Ax":{},"ScatterObj":{}}
        dictcopy = self.thread_dict[scanthreadname]['outdict'].copy() 
        grabd = basicfuncs.rawtowires(dictcopy,modstr)
        for i, poskey in enumerate(basicdata.pdict[modstr]): 
            plotobjects["ScatterObj"][poskey].remove()
            plotobjects["ScatterObj"][poskey] = plotobjects["Ax"][poskey].scatter(grabd[poskey],grabd[basicdata.sdict[modstr][i]],color="tab:blue")
            plotobjects["Canvas"][poskey].draw()