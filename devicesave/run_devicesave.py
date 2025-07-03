from devicesave import devicesave
ds = devicesave()
import time

devices = "devicesave/devicelist.txt"  # can also input a list, e.g. ["L:GR1LO","L:Q01","L:Q03",]
event = "p,100"              # must be in this format. "e,52" periodic is acceptable "p,100"
timer = 30                   # seconds for data to be recorded.
homedir = "C:/Users/erinchen/Documents/VS/Git_Projects/Linac_WireScan_Advanced/Data/DeviceSaves/"
savepath = homedir+str(round(time.time()))+"_AcceleratorBaseline_"+event.replace(",","")

ds.devicefetch(devices,event,timer,savepath)

