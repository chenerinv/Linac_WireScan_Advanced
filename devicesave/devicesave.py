import numpy as np
import acsys.dpm
import time
import itertools
import csv

class devicesave: 
    def __init__(self): 
        self.temp = []

    def devicefetch(self,devices,event,timer,savepath): 
        """Get average values of devices. devices is either a list of strings or a path to a txt file. 
        event is a string in the e,52 or p,100 format. timer is a number of seconds to record data. 
        savepath is a string path with file name (optional include .csv at end)."""

        async def multidevicefetch(con,devices,event,timer):
            # Setup context
            async with acsys.dpm.DPMContext(con) as dpm:
                # Add acquisition requests
                output = {}
                await dpm.add_entry(-1,"G:AMANDA.READING@p,1000") # so it won't stall if there are no beam events
                entrycount = 0
                for key in devices: 
                    output[entrycount] = {"request": key+".READING@"+event,"data": []}
                    output[entrycount+1] = {"request": key+".SETTING@"+event,"data": []}
                    await dpm.add_entry(entrycount,key+".READING@"+event)
                    await dpm.add_entry(entrycount+1,key+".SETTING@"+event)
                    entrycount=entrycount+2
                # Start acquisition
                await dpm.start()

                # Process incoming data
                inittime = time.time()
                async for evt_res in dpm:
                    if evt_res.isReading:
                        if evt_res.tag != -1: 
                            output[evt_res.tag]["data"].append(evt_res.data)
                    else:
                        # This is likely a status response
                        pass
                    if time.time()-inittime > timer: 
                        return output

        if isinstance(devices,str): 
            with open(devices,) as f: 
                devices = f.readlines()
                devices = [x.rstrip().strip() for x in devices]

        output1 = acsys.run_client(multidevicefetch,devices=devices,event=event,timer=timer)
        #print(output1)
        finaloutput = {
            "DeviceName": [],
            "Reading": [],
            "R Pts": [],
            "Reading STD": [],
            "Setting": [],
            "S Pts": [],
            "Setting STD": [],
            }
        for tag in list(output1.keys()): 
            devicestr = output1[tag]['request'].split('.')
            if output1[tag]['data'] == []: 
                avg = None
                leng = None
                std = None
            else: 
                avg = np.average(output1[tag]['data'])
                leng = len(output1[tag]['data'])
                std = np.std(output1[tag]['data'])

            if devicestr[0] not in finaloutput["DeviceName"]: 
                if (len(finaloutput["DeviceName"]) != len(finaloutput["Reading"])): 
                    finaloutput["Reading"].append(None)
                    finaloutput["R Pts"].append(None)
                    finaloutput["Reading STD"].append(None)
                if (len(finaloutput["DeviceName"]) != len(finaloutput["Setting"])):
                    finaloutput["Setting"].append(None)
                    finaloutput["S Pts"].append(None)
                    finaloutput["Setting STD"].append(None)
                finaloutput["DeviceName"].append(devicestr[0])
            if devicestr[1][:7] == "READING": 
                finaloutput["Reading"].append(avg)
                finaloutput["R Pts"].append(leng)
                finaloutput["Reading STD"].append(std)
            elif devicestr[1][:7] == "SETTING":
                finaloutput["Setting"].append(avg)
                finaloutput["S Pts"].append(leng)
                finaloutput["Setting STD"].append(std)

            if savepath[-4:] != ".csv": 
                savepath +=".csv"
            with open(savepath,"w",newline='') as f: # NOTE: the newline thing is because of windows & Python3. probably take out for non windows?
                csvw = csv.writer(f)
                csvw.writerow(finaloutput.keys())
                csvw.writerows(itertools.zip_longest(*finaloutput.values())) # zip would crop to the shortest list in the dict, using itertools instead
            f.close()

        return finaloutput