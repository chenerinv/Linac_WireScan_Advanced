import tkinter as tk
from tkinter import ttk, filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math
import os
import json
import time
import numpy as np

import basicdata
import basicfuncs
from acsyscontrol import acsyscontrol 
from dataanalysis import dataanalysis

class WireScanApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bunch Length Detector Data Collector")
        self.geometry("850x365")
        self.minsize(850,365)
        self.entries = {} # tk entries
        self.buttons = {} # tk buttons
        self.setpout = {} # dictionary with setup data
        self.metad = {} # dictionary with metadata
        self.readbacks = {} # dictionary for live readbacks
        self.pastreadbacks = {1:[], 2:[]} # reference info for killing and restarting a plot
        self.plotobjects1 = {"Frame":{},"Canvas":{},"Fig":{},"Ax":{},"ScatterObj":{}} # matplotlib objects
        self.acsyscontrol = acsyscontrol()
        self.datanalysis = dataanalysis()
        self.anaentries = {} # for analysis tab
        self.treedata = {} # for analysis tab

        # Create the tab control
        self.tabControl = ttk.Notebook(self)

        # Create Tab1
        self.tab1 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab1, text='Setup')
        self.tabControl.pack(expand=1, fill="both")
        self.tab1.columnconfigure(0,weight=0,minsize=545)
        self.tab1.columnconfigure(1,weight=1)
        self.tab1.rowconfigure(4,weight=1)

        # Create Tab3
        # self.tab3 = ttk.Frame(self.tabControl)
        # self.tabControl.add(self.tab3, text='Help')
        # self.tab3.columnconfigure(0,weight=1,minsize=425)
        # self.tab3.columnconfigure(1,weight=1,minsize=425)

        # Add widgets to Tab1
        self.create_widgets_in_tab1()
        # self.create_widgets_in_tab3()
        self.bind_all('<Button>', self.change_focus)
    
    def create_widgets_in_tab1(self): 
        # create subframes in tab1
        frame01 = ttk.Frame(self.tab1)
        frame01.grid(column=0,row=1,columnspan=1,pady=1,sticky="w")
        frame02 = ttk.LabelFrame(self.tab1,borderwidth=5,relief="solid",labelanchor="nw",text="Control")
        frame02.grid(column=0,row=2,columnspan=1,pady=1,sticky="w")
        frame04 = ttk.LabelFrame(self.tab1,borderwidth=5,relief="solid",labelanchor="n",text="Messages")
        frame04.grid(column=0,row=4,columnspan=1,pady=1,sticky="wes")
        frame10 = ttk.Frame(self.tab1,borderwidth=5,relief="solid")
        frame10.grid(column=1,row=0,columnspan=1,rowspan=5,pady=1,sticky="nesw")
        frame03 = ttk.LabelFrame(self.tab1,borderwidth=5,relief="solid",labelanchor="nw",text="Additional Parameter Readbacks")
        frame03.grid(column=0,row=3,columnspan=1,pady=1,sticky="w")

        # frame04
        s1 = tk.Scrollbar(frame04)
        s1.pack(side=tk.RIGHT,fill=tk.Y)
        text1 = tk.Text(frame04,height = 4,width=64,state="disabled",yscrollcommand=s1.set,wrap=tk.WORD)
        text1.pack(side=tk.LEFT,fill=tk.Y)
        self.entries["Messages"] = text1
        s1.config(command=text1.yview)

        # frame01
        frame010 = ttk.LabelFrame(frame01,borderwidth=5,relief="solid",labelanchor="nw",text="BLD Selection")
        frame010.grid(column=0,row=0,columnspan=1,pady=1,sticky="w")
        frame011 = ttk.LabelFrame(frame01,borderwidth=5,relief="solid",labelanchor="n",text="Readbacks")
        frame011.grid(column=1,row=0,columnspan=1,pady=1,sticky="n") # nested in frame 01, so must be made here not readbackpopup()

        # frame010
        labels = ["BLD","User Comment","Event","Additional Parameters"]
        for i, text in enumerate(labels):
            label = ttk.Label(frame010, text=text)
            if i<3: 
                label.grid(column=i, row=0, sticky='w', padx=2, pady=2)
            else: 
                label.grid(column=i-3, row=2, columnspan=3, sticky='w', padx=2, pady=2)
            ToolTip(label,basicdata.tooltips[text])
        combo010_0 = ttk.Combobox(frame010,state="readonly",values=list(basicdata.pdict.keys()),width=4) 
        combo010_0.grid(column=0, row=1, sticky='s', padx=2, pady=2)
        combo010_0.bind("<<ComboboxSelected>>", lambda event: self.selectedwire(frame011,frame10))
        self.entries[labels[0]] = combo010_0
        entry010_0 = ttk.Entry(frame010,width=25)
        entry010_0.grid(column=1, row=1, sticky='s', padx=2, pady=2)
        self.entries[labels[1]] = entry010_0
        combo010_1 = ttk.Combobox(frame010,state="readonly",values=basicdata.events,width=3)
        combo010_1.grid(column=2, row=1, sticky='s', padx=2, pady=2)
        self.entries[labels[2]] = combo010_1
        entry010_1 = ttk.Entry(frame010,width=40)
        entry010_1.grid(column=0,row=4, columnspan = 3,sticky="w",padx=2, pady=2)
        self.entries[labels[3]] = entry010_1

        # frame011 (Readbacks), frame10 (Plots)
            # blank unless selectedwire activates

        # frame03 (Additional Parameters)
            # blank unless scan is started

        # frame02
        text02 = "Save Directory"
        label02 = ttk.Label(frame02, text=text02)
        label02.grid(column=0, row=0, sticky='w', padx=5, pady=5)
        ToolTip(label02,basicdata.tooltips[text02])
        entry02 = ttk.Entry(frame02)
        entry02.grid(column=1, row=0, sticky='ew', padx=5, pady=2)
        self.entries[text02] = entry02
        browse_button_02 = ttk.Button(frame02, text='Browse', command=lambda e=entry02, t=text02: self.browse(e,t))
        browse_button_02.grid(column=2, row=0, sticky='w', padx=5, pady=2)
        self.buttons["Browse2"] = browse_button_02
        start_button = ttk.Button(frame02, text="Start", command= lambda: self.startbutton(frame03))
        start_button.grid(column=0, row=1, columnspan=1, padx=1, pady=1)
        self.buttons["Start"] = start_button
        stop_button = ttk.Button(frame02, text="Stop", command= lambda: self.stopbutton())
        stop_button.grid(column=1, row=1, columnspan=1, padx=1, pady=1)
        self.buttons["Stop"] = stop_button
        abort_button = ttk.Button(frame02, text="Abort", command=self.abortbutton)
        abort_button.grid(column=2, row=1, columnspan=1, padx=1, pady=1)
        self.buttons["Abort"] = abort_button

    def create_widgets_in_tab3(self):
        # create subframes in tab3
        frameh00 = ttk.LabelFrame(self.tab3,borderwidth=5,relief="solid",labelanchor="nw",text="General Help")
        frameh00.grid(column=0,row=0,columnspan=1,pady=1,sticky="nw")
        frameh01 = ttk.LabelFrame(self.tab3,borderwidth=5,relief="solid",labelanchor="nw",text="Stewardship")
        frameh01.grid(column=0,row=1,pady=1,sticky='w')
        frameh10 = ttk.LabelFrame(self.tab3,borderwidth=5,relief="solid",labelanchor='nw',text="Setup Parameters Help")
        frameh10.grid(column=1,row=0,columnspan=1,rowspan=2,pady=1,sticky="ne")

        # frameh00
        sh1 = tk.Scrollbar(frameh00)
        sh1.pack(side=tk.RIGHT,fill=tk.Y)
        texth1 = tk.Text(frameh00,height=11,state="disabled",yscrollcommand=sh1.set,wrap=tk.WORD,relief="flat")
        texth1.pack(side=tk.LEFT,fill=tk.Y)
        self.entries["Help1"] = texth1
        self.messageprint(basicdata.helpstrings[1],texth1)
        sh1.config(command=texth1.yview)

        # frameh10
        sh2 = tk.Scrollbar(frameh10)
        sh2.pack(side=tk.RIGHT,fill=tk.Y)
        texth2 = tk.Text(frameh10,height=18,state="disabled",yscrollcommand=sh2.set,wrap=tk.WORD,relief="flat")
        texth2.pack(side=tk.LEFT,fill=tk.Y)
        self.entries["Help2"] = texth2
        self.messageprint(basicdata.helpstrings[2],texth2)
        sh2.config(command=texth2.yview)

        # frameh01
        sh3 = tk.Scrollbar(frameh01)
        sh3.pack(side=tk.RIGHT,fill=tk.Y)
        texth3 = tk.Text(frameh01,height=4,state="disabled",yscrollcommand=sh3.set,wrap=tk.WORD,relief="flat")
        texth3.pack(side=tk.LEFT,fill=tk.Y)
        self.entries["Help3"] = texth3
        self.messageprint(basicdata.helpstrings[3],texth3)
        sh3.config(command=texth3.yview)

# commands:
    def testcalc(self): # to delete later, a temporary test button mapping
        print(self.acsyscontrol.get_list_of_threads())
        # # self.addparampopup()
        # print("--"+self.entries['Out Limit'].get().strip()+"--")
        print("yippee") 

    def change_focus(self,event):
        """Removes focus from previous focus when clicked elsewhere."""
        try: event.widget.focus_set()
        except: pass # TODO FIX THIS!!! it bugs out at the combobox...

    def browse(self, entry_widget, text):
        """Browse for a file."""
        if text == 'Save Directory':
            directory = filedialog.askdirectory()
            if directory:
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, directory)

    def messageprint(self,message,*widgets): 
        """Prints message to any supplied Text widget or defaults to main Message Box."""
        widget = self.entries["Messages"]
        for ar in widgets: # unpacks to get the widget
            widget = ar
        widget.config(state="normal")
        widget.insert(tk.END,message)
        widget.config(state="disabled")
        widget.see(tk.END)

    def selectedwire(self,frame011,frame10): 
        """Initiates all changes upon selecting a wire: changing limits, initiates live readbacks, initializes plot setup."""
        value = self.entries["BLD"].get().strip() # could have used event.widget.get() if we passed event through lambda
        self.readbackpopup(value,frame011) #technically could get value in these, but it is easier to just pass it?
        self.plotinit(value,frame10)

    def plotinit(self,value,frame10): 
        '''Initializing axes of the live plot upon wire selection & deleting previous subplots.'''
        # deleting existing frames, canvas, figs        
        for widgets in frame10.winfo_children(): # delete eveyrthing in frame
            widgets.destroy()
        # resetting the dictionary of stuff
        plotobj = {"Frame":{},"Canvas":{},"Fig":{},"Ax":{},"ScatterObj":{}}
        # building and saving all needed objects in plotobjects
        j = 0
        if value == 0: g = basicdata.plots
        else: g = basicdata.pdict[value]

        for i,key in enumerate(g): 
            plotobj["Frame"][key] = ttk.Frame(frame10)
            plotobj["Frame"][key].grid(column=0,row=j,columnspan=1,pady=1,sticky="we")
            frame10.rowconfigure(j,weight=1)
            j = j+1
            plotobj["Fig"][key] = Figure(dpi=100)
            plotobj["Canvas"][key] = FigureCanvasTkAgg(plotobj["Fig"][key], master=plotobj["Frame"][key])
            plotobj["Canvas"][key].draw()
            plotobj["Canvas"][key].get_tk_widget().pack(expand=1,fill="both")
            plotobj["Ax"][key] = plotobj["Fig"][key].add_subplot(111)
            if value == 0: 
                plotobj["Ax"][key].set_xlabel("Trombone phase (deg@201 MHz)",fontsize=9)
                plotobj["Ax"][key].set_ylabel("EMT Signal (V)",fontsize=9)
            else: 
                plotobj["Ax"][key].set_xlabel(key,fontsize=9)
                plotobj["Ax"][key].set_ylabel(basicdata.sdict[value][i],fontsize=9)
            plotobj["Ax"][key].tick_params(axis='x',labelsize=8)
            plotobj["Ax"][key].tick_params(axis='y',labelsize=8)
            plotobj["ScatterObj"][key] = plotobj["Ax"][key].scatter([],[],color="tab:blue")
            plotobj["Canvas"][key].draw()          
            plotobj["Fig"][key].set_tight_layout(True) 
        frame10.columnconfigure(0,weight=1)
        self.plotobjects1 = plotobj

    def readbackpopup(self,value,frame011):
        """Populate a frame with wire position and signal readbacks everytime a wire is selected."""
        # delete everything in frame
        for widgets in frame011.winfo_children(): 
            widgets.destroy()
        # access the last readbacks keys and deletes them from being read anymore.
        # readbackpopup() and additionalparampopup() share the same dictionary & thread for reading parameters, which is why
        # we have to be specific about which keys are deleted.
        for key in self.pastreadbacks[1]: 
            if key in list(self.readbacks.keys()): 
                del self.readbacks[key]
        # create and print readbacks. StringVar to let it be changeable
        params = basicdata.allparams[value]
        units = basicdata.unitlist
        for i, text in enumerate(params):
            label = ttk.Label(frame011, text=text+":")
            label.grid(column=(i%2)*3, row=math.floor(i/2), sticky='n', padx=0, pady=2)
            self.readbacks[text] = tk.StringVar()
            self.pastreadbacks[1].append(text)
            label1 = ttk.Label(frame011, textvariable=self.readbacks[text]) 
            label1.grid(column=(i%2)*3+1, row=math.floor(i/2), sticky='n', padx=0, pady=2)
            label2 = ttk.Label(frame011, text=units[i])
            label2.grid(column=(i%2)*3+2, row=math.floor(i/2), sticky='n', padx=2, pady=2)

        # start the thread to fetch and plot readbacks
        self.start_readback_thread()

    def addparampopup(self,frame03,paramstrlist): 
        """Populate a frame with additional parameters everytime a scan is started."""
        # delete everything in frame
        for widgets in frame03.winfo_children(): 
            widgets.destroy()
        # change GUI window size based on how many parameters we're adding
        if paramstrlist == []: 
            self.minsize(850,365)
            frame03.grid_remove()
        elif len(paramstrlist) < 5: 
            self.minsize(850,410) 
            frame03.grid()
        else: 
            self.minsize(850,430) 
            frame03.grid()
        # clear the parameters that were being fetched last time the program had this popup
        for key in self.pastreadbacks[2]: 
            if key in list(self.readbacks.keys()): 
                del self.readbacks[key]
        # print the parameters needed
        for i, text in enumerate(paramstrlist):
            if i == 8: 
                break
            j = i%4 * 3
            k = math.floor(i/4) 
            label = ttk.Label(frame03, text=text+":")
            label.grid(column=j, row=k, sticky='n', padx=0, pady=2)
            self.readbacks[text] = tk.StringVar()
            self.pastreadbacks[2].append(text)
            label1 = ttk.Label(frame03, textvariable=self.readbacks[text]) 
            label1.grid(column=j+1, row=k, sticky='n', padx=2, pady=2)
            # label2 = ttk.Label(frame14, text=" mm") #TODO find way to fetch units
            # label2.grid(column=j+2, row=k, sticky='n', padx=2, pady=2)
        # start the readbacks thread
        self.start_readback_thread()

    def start_readback_thread(self): 
        """Start the readback thread and clear it if already existent. Shares fetching for readbackpopup and addparampopup."""
        self.readback_thread = "allreadbacks"
        if self.readback_thread in self.acsyscontrol.get_list_of_threads(): # kill existing thread if present
            self.acsyscontrol.end_any_thread(self.readback_thread)
        self.acsyscontrol.start_readbacks_thread(self.readback_thread,self.readbacks)

    def checkentriescorrect(self, indict): 
        """Check if a dictionary's values are appropriate for their keys & parses them to the correct data type. 
        Executes the main logic of approval system prior to a Start or after Upload. 
        Input a dictionary, output either False (if something's incorrect) or a dictionary of the appropriate data types.
        """
        outdict = {}
        for key in list(indict.keys()): 
            if key in basicdata.skippedkeys: # skipping the ones irrelevant to setup
                continue
            try: 
                tval = indict[key].get().strip()
            except AttributeError: 
                tval = indict[key]
            except: 
                print(key)
            ctype = basicdata.checkcorrect[key]
            tf, tval = basicfuncs.checktype(tval,ctype)
            if tf is False: 
                self.messageprint(key+" is not of appropriate data type "+str(ctype)+".\n")
            if key == "BLD": 
                tval = tval.strip()
                if tval not in list(basicdata.pdict.keys()): 
                    self.messageprint(tval+" is an invalid wire.\n")
                    return False
            elif key == "Event": 
                tval = tval.strip()
                if tval not in basicdata.events: 
                    self.messageprint(tval+" is an invalid event.\n")
                    return False
            elif key == "Additional Parameters": 
                tval = tval.split(',')
                for i,item in list(enumerate(tval)): tval[i] = item.strip()
                tval = [i for i in tval if i != ""] # clearing empty entries
            elif key == "Save Directory": 
                if os.path.isdir(tval) is False: 
                    self.messageprint(tval+" is not a directory.\n")
                    return False
            outdict[key] = tval
        return outdict

    def lockentries(self,statestr,entrykeys,buttonkeys): 
        """Enable and disable buttons and entry widgets in the Tkinter GUI."""
        for entry in entrykeys: 
            self.entries[entry].config(state=statestr)
        for button in buttonkeys: 
            self.buttons[button].config(state=statestr)

    def startbutton(self,frame14): 
        """Execute the setup needed for a scan and start the scan."""
        # locking to modification
        self.lockentries("disabled",basicdata.lockedentries,basicdata.lockedbuttons) 
        self.scan_thread = "mainscan"
        # check thread isn't open+unset or open+set+incomplete
        if self.scan_thread in self.acsyscontrol.get_list_of_threads(): # if thread exists and is unset
            self.messageprint("Starting another scan is not allowed. Another scan is ongoing.\n")
            self.lockentries("enabled",basicdata.lockedentries,basicdata.lockedbuttons)
            return
        elif self.acsyscontrol.check_finally(self.scan_thread) is False:  # or if thread exists, is set, but finally isn't done (to accomodate lack of joining in abort)
            self.messageprint("Starting another scan is not allowed. Another scan is closing.\n")
            self.lockentries("enabled",basicdata.lockedentries,basicdata.lockedbuttons)
            return
        # main check to see if the setup is appropriate
        self.setpout = self.checkentriescorrect(self.entries) 
        if self.setpout == False: 
            self.lockentries("enabled",basicdata.lockedentries,basicdata.lockedbuttons)
            return
        # checking there's no missing keys
        for item in basicdata.requiredkeys: 
            if item not in list(self.setpout.keys()): 
                self.messageprint(item+" is a required value.\n")
                self.lockentries("enabled",basicdata.lockedentries,basicdata.lockedbuttons)
                return
        # add new frame with additional readbacks
        self.addparampopup(frame14,self.setpout["Additional Parameters"])              
        
        print(self.setpout)

        # things that doesn't need to be saved in setup parameters (some still are) but needs to be accessible by scan
        self.setpout["Timestamp"] = round(time.time()) # choose unix time stamp around now 
        # make directory
        savepath = os.path.join(self.setpout["Save Directory"],str(self.setpout["Timestamp"])+"_"+self.setpout["BLD"]).replace("\\","/")
        if not os.path.exists(savepath): 
            os.makedirs(savepath)
            self.setpout["BLD Directory"] = savepath
        else: 
            self.messageprint("Folder for data unable to be created.\n")
            self.lockentries("enabled",basicdata.lockedentries,basicdata.lockedbuttons)
            return
        basicfuncs.dicttojson(self.setpout,os.path.join(self.setpout["BLD Directory"],"_".join([str(self.setpout["Timestamp"]),self.setpout["BLD"],"SetupParameters.json"])))
        # make dict of tags
        tagdict, i = {}, 1
        for device in basicdata.allparams[self.setpout['BLD']]+basicdata.sdict[self.setpout['BLD']]+self.setpout['Additional Parameters']:
            tagdict[i]=device
            i=i+1
        self.setpout["Tags"] = tagdict

        # collect metadata 
        self.metad = {key:self.setpout[key] for key in ['Event', 'User Comment','Timestamp','BLD Directory','Tags']}
        if self.setpout["Event"] == "0A": 
            params = ["L:SOURCE.READING","L:D7TOR.READING","L:TCHTON.READING","L:TCHTOF.READING","L:BSTUDY.READING"]
        else: 
            params = ["L:SOURCE.READING","L:D7TOR.READING"]
        m = self.acsyscontrol.checkparam(params,10)
        if m[0] == -10.24:
            self.metad["Source"] = "A"
        elif m[0] == 10.24: 
            self.metad["Source"] = "B"
        self.metad["L:D7TOR"] = m[1]
        if len(params) == 5: 
            self.metad["Pulse Length"] = m[3]-m[2]
            self.metad["Frequency"] = m[4]
        self.metad["Abort"] = False
        basicfuncs.dicttojson(self.metad,os.path.join(self.setpout["BLD Directory"],"_".join([str(self.setpout["Timestamp"]),self.setpout["BLD"],"Metadata.json"])))
        
        # start wirescan 
        self.plot_thread = "liveplot" 
        self.acsyscontrol.start_scan_thread(self.scan_thread,self.setpout,self.lockentries,self.messageprint,self.plot_thread)
        self.messageprint("Scan initiated.\n")
        # start plotting here
        if self.plot_thread in self.acsyscontrol.get_list_of_threads(): 
            self.acsyscontrol.end_any_thread(self.plot_thread)
        print("Starting liveplot")
        self.acsyscontrol.start_liveplot_thread(self.plot_thread,self.scan_thread,self.setpout["BLD"],self.plotobjects1) 

    def abortbutton(self): 
        """Abort an ongoing scan."""
        try: 
            if self.scan_thread in self.acsyscontrol.get_list_of_threads(): # kill existing thread if present
                self.acsyscontrol.end_any_thread(self.scan_thread)
                self.messageprint("Scan aborted by user.\n") 
                self.wiresout() # think more about this
                # record that an abort occurred by editing the metadata file
                self.metad["Abort"] = True
                basicfuncs.dicttojson(self.metad,os.path.join(self.setpout["BLD Directory"],"_".join([str(self.setpout["Timestamp"]),self.setpout["BLD"],"Metadata.json"])))
            else: 
                self.messageprint("No scan to abort.\n")
        except AttributeError: 
            self.messageprint("No scan to abort.\n") 

    def stopbutton(self): 
        pass


class ToolTip(): 
    """Show small description popups when hovering over specific labels."""
    # this entire class is from https://stackoverflow.com/questions/3221956/how-do-i-display-tooltips-in-tkinter
    def __init__(self, widget, text='widget info'): 
        self.waittime = 500
        self.wraplength = 180
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy= self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()

if __name__ == "__main__":
    app = WireScanApp()
    app.mainloop()