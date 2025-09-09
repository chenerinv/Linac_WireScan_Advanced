import threading
import acsys.dpm
import os
import basicdata
import basicfuncs
import time
from dataanalysis import dataanalysis    

async def runscan(con): 
# setup context
    async with acsys.dpm.DPMContext(con,dpm_node="DPM03") as dpm:   

        # try: 
        await dpm.enable_settings(role='testing') #TODO UNCOMMENT WHEN ALLOWED TO MOVE WS!!!
        # except: 
        #     print("Invalid Kerberos realm.\n")  #TODO change to messageprint
        #     return

        # # for key in maindict['Tags'].keys(): 
        # #     await dpm.add_entry(key,maindict['Tags'][key]+"@e,"+maindict['Event'])
        # # await dpm.add_entry(0,"L:C0VPA@p,1H") # need this to stop it from lagging unbearably

        # await dpm.add_entry(0,"G:AMANDA.SETTING")
        # await dpm.add_entry(1,"L:D01BDS@e,0A")
        # await dpm.add_entry(2,"L:GR1MID@e,0A")

        # await dpm.start()

        # numread = 10
        # settingslist = [0,1,2,3,4,5]
        # countlist = {0: 0, 
        #              1: 0,
        #              2: 0,}
        # setcount = 0
        # outdata = {"tag": [],
        #            "data": [],
        #            "stamp": []}
        
        # await dpm.apply_settings([0,settingslist[setcount]])
        # print("set "+settingslist[setcount])
        # setcount+=1
        # async for evt_res in dpm: 

        #     if evt_res.isReading: 
        #         if countlist[evt_res.tag] <= numread:
        #             print(evt_res.tag,evt_res.data,countlist[evt_res.tag])
        #             countlist[evt_res.tag]+=1
        #             # limit saving data only to 10 maybe? or save all data the traditional way and the reformatted way
            
        #     checkpass = 1
        #     for key in list(countlist.keys()): 
        #         if countlist[key] != 10: 
        #             checkpass = 0
        #             break
        #     if checkpass == 1: 
        #         await dpm.apply_settings([0,settingslist[setcount]])
        #         print("set "+settingslist[setcount])
        #         setcount+=1

acsys.run_client(runscan)