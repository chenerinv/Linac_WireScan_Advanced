import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import basicdata
import basicfuncs
from acsyscontrol import acsyscontrol 

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backend_bases import key_press_handler

#from matplotlib import style

import numpy as np
import math
import os
import json
import time

class WireScanApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fast Wire Scan App")
        self.geometry("850x365")
        self.minsize(850,365)
        self.entries = {}
        self.buttons = {}
        self.setpout = {}
        self.metad = {}
        self.readbacks = {}
        self.pastreadbacks = {1:[], 2:[]}
        self.acsyscontrol = acsyscontrol()
        self.plotobjects = {"Frame":{},"Canvas":{},"Fig":{},"Ax":{},"ScatterObj":{}}

        # want to deprecate these
        self.plots = {}
        self.scatterobj = {}

        # Create the tab control
        self.tabControl = ttk.Notebook(self)

        # Create Tab1
        self.tab1 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab1, text='Setup')
        self.tabControl.pack(expand=1, fill="both")
        self.tab1.columnconfigure(0,weight=0,minsize=480)
        self.tab1.columnconfigure(1,weight=1)
        self.tab1.rowconfigure(4,weight=1)

        # Create Tab2
        self.tab2 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab2, text='Analysis')

        # Create Tab3
        self.tab3 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab3, text='Help')
        self.tab3.columnconfigure(0,weight=1,minsize=425)
        self.tab3.columnconfigure(1,weight=1,minsize=425)

        # Create Advanced Parameters Window (hidden)
        self.AdvChild = Adv_Window(self)
        self.AdvChild.withdraw()

        # Add widgets to Tab1
        self.create_widgets_in_tab1()
        self.create_widgets_in_tab3()
        self.bind_all('<Button>', self.change_focus)
    
    def create_widgets_in_tab1(self): 
        # create subframes in tab1
        frame11 = ttk.LabelFrame(self.tab1,borderwidth=5,relief="solid",labelanchor="nw",text="Quick Setup")
        frame11.grid(column=0,row=0,columnspan=1,pady=1,sticky="nw")
        frame12 = ttk.Frame(self.tab1)
        frame12.grid(column=0,row=1,columnspan=1,pady=1,sticky="w")
        frame13 = ttk.LabelFrame(self.tab1,borderwidth=5,relief="solid",labelanchor="nw",text="Control")
        frame13.grid(column=0,row=2,columnspan=1,pady=1,sticky="w")
        frame15 = ttk.LabelFrame(self.tab1,borderwidth=5,relief="solid",labelanchor="n",text="Messages")
        frame15.grid(column=0,row=4,columnspan=1,pady=1,sticky="wes")
        frame21 = ttk.Frame(self.tab1,borderwidth=5,relief="solid")
        frame21.grid(column=1,row=0,columnspan=1,rowspan=5,pady=1,sticky="nesw")
        frame14 = ttk.LabelFrame(self.tab1,borderwidth=5,relief="solid",labelanchor="nw",text="Additional Parameter Readbacks")
        frame14.grid(column=0,row=3,columnspan=1,pady=1,sticky="w")

        # frame14
        s1 = tk.Scrollbar(frame15)
        s1.pack(side=tk.RIGHT,fill=tk.Y)
        text1 = tk.Text(frame15,height = 4,width=56,state="disabled",yscrollcommand=s1.set,wrap=tk.WORD)
        text1.pack(side=tk.LEFT,fill=tk.Y)
        self.entries["Messages"] = text1
        s1.config(command=text1.yview)
        frame121 = ttk.LabelFrame(frame12,borderwidth=5,relief="solid",labelanchor="nw",text="Wire")
        frame121.grid(column=0,row=0,columnspan=1,pady=1,sticky="w")
        frame122 = ttk.LabelFrame(frame12,borderwidth=5,relief="solid",labelanchor="nw",text="Readbacks")
        frame122.grid(column=1,row=0,columnspan=1,pady=1,sticky="e") 
        # note frame122 can't be made within readbackpopup() because it is nested in frame12
        # however, frame 14 can be made in its function because its up a level.

        # frame11
        text11 = "Setup Parameters"
        label11 = ttk.Label(frame11, text=text11)
        label11.grid(column=0, row=0, sticky='w', padx=5, pady=5)
        ToolTip(label11,basicdata.tooltips[text11])
        entry11 = ttk.Entry(frame11)
        entry11.grid(column=1, row=0, sticky='ew', padx=5, pady=2)
        self.entries[text11] = entry11
        button11 = ttk.Button(frame11, text='Browse', command=lambda e=entry11, t=text11: self.browse(e,t))
        button11.grid(column=2, row=0, padx=5, pady=2)
        self.buttons["Browse1"] = button11
        upload_button = ttk.Button(frame11, text='Upload', command=lambda: self.loadsetp(frame122,frame21)) #TODO remove & integrate into browse1
        upload_button.grid(column=3, row=0, sticky='e', padx=5, pady=2)
        self.buttons["Upload"] = upload_button

        # frame121
        labels = ["Wire","Out Limit","In Limit", "Event"]
        for i, text in enumerate(labels):
            label = ttk.Label(frame121, text=text)
            label.grid(column=i, row=0, sticky='n', padx=2, pady=2)
            ToolTip(label,basicdata.tooltips[text])
        entry1 = ttk.Entry(frame121,width=8)
        entry1.grid(column=1, row=1, sticky='s', padx=2, pady=2)
        self.entries[labels[1]] = entry1
        entry2 = ttk.Entry(frame121,width=8)
        entry2.grid(column=2, row=1, sticky='s', padx=2, pady=2)
        self.entries[labels[2]] = entry2
        combo1 = ttk.Combobox(frame121,state="readonly",values=list(basicdata.pdict.keys()),width=4) 
        combo1.grid(column=0, row=1, sticky='s', padx=2, pady=2)
        combo1.bind("<<ComboboxSelected>>", lambda event: self.selectedwire(frame122,frame21))
        self.entries[labels[0]] = combo1
        combo2 = ttk.Combobox(frame121,state="readonly",values=basicdata.events,width=3)
        combo2.grid(column=3, row=1, sticky='s', padx=2, pady=2)
        self.entries[labels[3]] = combo2
        adv_button = ttk.Button(frame121, text="Advanced Settings", command=self.open_advwindow)
        adv_button.grid(column=0, row=2, columnspan=4, padx=1, pady=1)

        # frame 122
            # blank unless selectedwire activates

        # frame13
        text13 = "Save Directory"
        label13 = ttk.Label(frame13, text=text13)
        label13.grid(column=0, row=0, sticky='w', padx=5, pady=5)
        ToolTip(label13,basicdata.tooltips[text13])
        entry13 = ttk.Entry(frame13)
        entry13.grid(column=1, row=0, sticky='ew', padx=5, pady=2)
        self.entries[text13] = entry13
        button13 = ttk.Button(frame13, text='Browse', command=lambda e=entry13, t=text13: self.browse(e,t))
        button13.grid(column=2, row=0, sticky='w', padx=5, pady=2)
        self.buttons["Browse2"] = button13
        start_button = ttk.Button(frame13, text="Start", command= lambda: self.startbutton(frame14))
        start_button.grid(column=0, row=1, columnspan=1, padx=1, pady=1)
        self.buttons["Start"] = start_button
        wout_button = ttk.Button(frame13, text="Wires Out", command=self.wiresout)
        wout_button.grid(column=1, row=1, columnspan=1, padx=1, pady=1)
        self.buttons["Wires Out"] = wout_button
        abort_button = ttk.Button(frame13, text="Abort", command=self.abortbutton)
        abort_button.grid(column=2, row=1, columnspan=1, padx=1, pady=1)
        self.buttons["Abort"] = abort_button

        # frame21
        # empty until a wire is selected

    def create_widgets_in_tab3(self):
        frameh11 = ttk.LabelFrame(self.tab3,borderwidth=5,relief="solid",labelanchor="nw",text="General Help")
        frameh11.grid(column=0,row=0,columnspan=1,pady=1,sticky="nw")
        frameh21 = ttk.LabelFrame(self.tab3,borderwidth=5,relief="solid",labelanchor='nw',text="Setup Parameters Help")
        frameh21.grid(column=1,row=0,columnspan=1,rowspan=2,pady=1,sticky="ne")
        frameh12 = ttk.LabelFrame(self.tab3,borderwidth=5,relief="solid",labelanchor="nw",text="Stewardship")
        frameh12.grid(column=0,row=1,pady=1,sticky='w')

        sh1 = tk.Scrollbar(frameh11)
        sh1.pack(side=tk.RIGHT,fill=tk.Y)
        texth1 = tk.Text(frameh11,height=4,state="disabled",yscrollcommand=sh1.set,wrap=tk.WORD)
        texth1.pack(side=tk.LEFT,fill=tk.Y)
        self.entries["Help1"] = texth1
        self.messageprint(basicdata.helpstrings[1],texth1)
        sh1.config(command=texth1.yview)

        sh3 = tk.Scrollbar(frameh12)
        sh3.pack(side=tk.RIGHT,fill=tk.Y)
        texth3 = tk.Text(frameh12,height=4,state="disabled",yscrollcommand=sh3.set,wrap=tk.WORD)
        texth3.pack(side=tk.LEFT,fill=tk.Y)
        self.entries["Help3"] = texth3
        self.messageprint(basicdata.helpstrings[3],texth3)
        sh3.config(command=texth3.yview)

        sh2 = tk.Scrollbar(frameh21)
        sh2.pack(side=tk.RIGHT,fill=tk.Y)
        texth2 = tk.Text(frameh21,height=10,state="disabled",yscrollcommand=sh2.set,wrap=tk.WORD)
        texth2.pack(side=tk.LEFT,fill=tk.Y)
        self.entries["Help2"] = texth2
        self.messageprint(basicdata.helpstrings[2],texth2)
        sh2.config(command=texth2.yview)

##### COMMANDS:
    def testcalc(self): # to delete later, a temporary test button mapping
        print(self.acsyscontrol.get_list_of_threads())
        # # self.addparampopup()
        # print("--"+self.entries['Out Limit'].get().strip()+"--")
        print("yippee") 

    def change_focus(self,event):
        """Removes focus from previous focus when clicked elsewhere. #TODO buggy on the combobox deselect."""
        try: event.widget.focus_set()
        except: pass # TODO FIX THIS!!! it bugs out at the combobox...

    def open_advwindow(self):
        """Open pop-up window with Advanced Parameters. Steals focus until window is closed."""
        self.AdvChild.deiconify()
        self.AdvChild.grab_set() # keep focus on advanced param window

    def browse(self, entry_widget, text):
        if text == 'Setup Parameters':
            filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
            if filename:
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, filename)
                self.workdir = os.path.dirname(filename)
            
        elif text == 'Save Directory':
            directory = filedialog.askdirectory()
            if directory:
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, directory)

    def changelims(self, keywidget, value):
        widget1 = self.entries[keywidget]
        widget1.delete(0, tk.END)
        if keywidget == "Out Limit": 
            widget1.insert(tk.END, basicdata.outlimdict[value])
        elif keywidget == "In Limit":
            widget1.insert(tk.END, basicdata.inlimdict[value])

    def messageprint(self,message,*widgets): 
        """Prints message to any supplied Text widget."""
        widget = self.entries["Messages"]
        for ar in widgets: 
            widget = ar
        widget.config(state="normal")
        widget.insert(tk.END,message)
        widget.config(state="disabled")
        widget.see(tk.END)

    def selectedwire(self,frame122,frame21): 
        value = self.entries["Wire"].get().strip() # could have used event.widget.get() if we passed event through lambda
        self.changelims("Out Limit",value)
        self.changelims("In Limit",value)
        self.readbackpopup(value,frame122) #technically could get value in these, but it is easier to just pass it?
        self.plotinit(value,frame21)

    def plotinit(self,value,frame21): 
        '''Initializing axes of the live plot upon wire selection & deleting previous subplots.'''
        # deleting existing frames, canvas, figs        
        for widgets in frame21.winfo_children(): # delete eveyrthing in frame
            widgets.destroy()
        # resetting the dictionary of stuff
        self.plotobjects = {"Frame":{},"Canvas":{},"Fig":{},"Ax":{},"ScatterObj":{}}

        j = 0
        for i,key in enumerate(basicdata.pdict[value]): 
            self.plotobjects["Frame"][key] = ttk.Frame(frame21)
            self.plotobjects["Frame"][key].grid(column=0,row=j,columnspan=1,pady=1,sticky="we")
            frame21.rowconfigure(j,weight=1)
            j = j+1
            self.plotobjects["Fig"][key] = Figure(dpi=100)
            self.plotobjects["Canvas"][key] = FigureCanvasTkAgg(self.plotobjects["Fig"][key], master=self.plotobjects["Frame"][key])
            self.plotobjects["Canvas"][key].draw()
            self.plotobjects["Canvas"][key].get_tk_widget().pack(expand=1,fill="both")
            self.plotobjects["Ax"][key] = self.plotobjects["Fig"][key].add_subplot(111)
            self.plotobjects["Ax"][key].set_xlabel(key,fontsize=9)
            self.plotobjects["Ax"][key].set_ylabel(basicdata.sdict[value][i],fontsize=9)
            self.plotobjects["Ax"][key].tick_params(axis='x',labelsize=8)
            self.plotobjects["Ax"][key].tick_params(axis='y',labelsize=8)
            self.plotobjects["ScatterObj"][key] = self.plotobjects["Ax"][key].scatter([],[],color="tab:blue")
            self.plotobjects["Canvas"][key].draw()          
            self.plotobjects["Fig"][key].set_tight_layout(True) 
        frame21.columnconfigure(0,weight=1)
        #TODO consider adding navigation toolbar...fix plot...something

    def readbackpopup(self,value,frame122):
        """Populate a frame with wire position and signal readbacks everytime a wire is selected."""
        for widgets in frame122.winfo_children(): # delete eveyrthing in frame
            widgets.destroy()

        for key in self.pastreadbacks[1]: 
            if key in list(self.readbacks.keys()): 
                del self.readbacks[key]

        pos, sig = basicdata.pdict[value], basicdata.sdict[value]
        for i, text in enumerate(pos):
            label = ttk.Label(frame122, text=text+":")
            label.grid(column=0, row=i, sticky='n', padx=0, pady=2)
            self.readbacks[text] = tk.StringVar()
            self.pastreadbacks[1].append(text)
            label1 = ttk.Label(frame122, textvariable=self.readbacks[text]) # these should be "6.23 mm" etc
            label1.grid(column=1, row=i, sticky='n', padx=0, pady=2)
            label2 = ttk.Label(frame122, text=" mm")
            label2.grid(column=2, row=i, sticky='n', padx=2, pady=2)
        for i, text in enumerate(sig):
            label = ttk.Label(frame122, text=text+":")
            label.grid(column=3, row=i, sticky='n', padx=2, pady=2)
            self.readbacks[text] = tk.StringVar()
            self.pastreadbacks[1].append(text)
            label1 = ttk.Label(frame122, textvariable=self.readbacks[text]) 
            label1.grid(column=4, row=i, sticky='n', padx=0, pady=2)
            label2 = ttk.Label(frame122, text=" V")
            label2.grid(column=5, row=i, sticky='n', padx=0, pady=2)
        
        self.start_readback_thread()

    def addparampopup(self,frame14,paramstrlist): 
        for widgets in frame14.winfo_children(): # delete eveyrthing in frame
            widgets.destroy()
        if paramstrlist == []: 
            self.minsize(850,365)
            frame14.grid_remove()
        elif len(paramstrlist) < 5: 
            self.minsize(850,410) # GUI adjustment for new section
            frame14.grid()
        else: 
            self.minsize(850,430) # GUI adjustment for new section
            frame14.grid()

        for key in self.pastreadbacks[2]: # clear the parameters that were being fetched last time the program had this popup
            if key in list(self.readbacks.keys()): 
                del self.readbacks[key]

        for i, text in enumerate(paramstrlist):
            if i == 8: 
                break
            j = i%4 * 3
            k = math.floor(i/4) 
            label = ttk.Label(frame14, text=text+":")
            label.grid(column=j, row=k, sticky='n', padx=0, pady=2)
            self.readbacks[text] = tk.StringVar()
            self.pastreadbacks[2].append(text)
            label1 = ttk.Label(frame14, textvariable=self.readbacks[text]) # these should be "6.23" etc
            label1.grid(column=j+1, row=k, sticky='n', padx=2, pady=2)
            # label2 = ttk.Label(frame14, text=" mm") #TODO find way to fetch units
            # label2.grid(column=j+2, row=k, sticky='n', padx=2, pady=2)

        self.start_readback_thread()

    def start_readback_thread(self): 
        """Start the readback thread and clear it if already existent."""
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

            if key == "Wire": 
                tval = tval.strip()
                if tval not in list(basicdata.pdict.keys()): 
                    self.messageprint(tval+" is an invalid wire.\n")
                    return False
            elif key == "Event": 
                tval = tval.strip()
                if tval not in basicdata.events: 
                    self.messageprint(tval+" is an invalid event.\n")
                    return False
            elif key == "WS Mode": 
                tval = tval.strip()
                if tval not in basicdata.wsmodes: 
                    self.messageprint(tval+" is an invalid WS Mode.\n")
                    return False
            elif key == "Additional Parameters": 
                tval = tval.split(',')
                for i,item in list(enumerate(tval)): tval[i] = item.strip()
                tval = [i for i in tval if i != ""] # clearing empty entries
            elif key == "Steps": 
                if tval < 0: 
                    self.messageprint(key+" must be a positive value.\n")
                    return False
            elif key == "Monitors": 
                tval = tval.split(',')
                for i,item in list(enumerate(tval)): tval[i] = item.strip()
                tval = [i for i in tval if i != ""]
                if "Monitor Max" in list(outdict.keys()): 
                    if len(tval) != len(outdict["Monitor Max"]): 
                        self.messageprint("Monitors should have the same number of entries as Monitor Max.\n")
                        return False
                if "Monitor Min" in list(outdict.keys()):
                    if len(tval) != len(outdict["Monitor Min"]): 
                        self.messageprint("Monitors should have the same number of entries as Monitor Min.\n")
                        return False
            elif (key == "Monitor Min") or (key == "Monitor Max"):
                tval = tval.split(',')
                for i,item in list(enumerate(tval)): tval[i] = item.strip()
                tval = [i for i in tval if i != ""]
                for i, item in enumerate(tval): 
                    tf2, tval[i] = basicfuncs.checktype(item,float)
                    if tf2 is False: 
                        self.messageprint("One value in "+key+" is not of appropriate data type "+str(float)+".\n")
                        return False
                if key == "Monitor Min": 
                    if "Monitor Max" in list(outdict.keys()): 
                        if len(tval) != len(outdict["Monitor Max"]): 
                            self.messageprint("Monitor Min should have the same number of entries as Monitor Max.\n")
                            return False
                        for i,item in enumerate(tval):
                            if item > outdict["Monitor Max"][i]: 
                                self.messageprint("Monitor Min should be smaller than Monitor Max.\n")
                                return False
                    if "Monitors" in list(outdict.keys()):
                        if len(tval) != len(outdict["Monitors"]): 
                            self.messageprint("Monitor Min should have the same number of entries as Monitors.\n")
                            return False
                elif key == "Monitor Max": 
                    if "Monitor Min" in list(outdict.keys()): 
                        if len(tval) != len(outdict["Monitor Min"]): 
                            self.messageprint("Monitor Max should have the same number of entries as Monitor Min.\n")
                            return False
                        for i,item in enumerate(tval):
                            if item < outdict["Monitor Min"][i]: 
                                self.messageprint("Monitor Min should be smaller than Monitor Max.\n")
                                return False
                    if "Monitors" in list(outdict.keys()):
                        if len(tval) != len(outdict["Monitors"]): 
                            self.messageprint("Monitor Max should have the same number of entries as Monitors.\n")
                            return False
            elif key == "Save Directory": 
                if os.path.isdir(tval) is False: 
                    self.messageprint(tval+" is not a directory.\n")
                    return False
            elif key == "Out Limit": 
                if "In Limit" in list(outdict.keys()): 
                    if tval > outdict["In Limit"]: 
                        self.messageprint("Out Limit should be smaller than In Limit.\n")
                        return False        
            elif key == "In Limit": 
                if "Out Limit" in list(outdict.keys()): 
                    if tval < outdict["Out Limit"]: 
                        self.messageprint("Out Limit should be smaller than In Limit.\n")
                        return False
            outdict[key] = tval
        return outdict

    def loadsetp(self,frame122,frame21): # need to get frame out of this & have it accessible globally? 
        """Function for the Upload button. 
        Executes necessary actions to upload data from a JSON to the program & GUI. 
        Confirms entries are appropriate.
        """
        filepath = self.entries['Setup Parameters'].get().strip()
        if filepath == "": 
            self.messageprint("Please add the path to a Setup Parameters file before pressing upload.\n")
            return
        else: 
            try: 
                with open(filepath) as json_file:
                    tempinput = json.load(json_file)
            except: 
                self.messageprint("This file is not valid. Please try again.\n")
                return

            for ignorekey in basicdata.ignorekeys: # skipping the additional keys in Setup Params
                if ignorekey in list(tempinput.keys()): 
                    del tempinput[ignorekey]
            cinkeys = list(tempinput.keys())
            for key in cinkeys: 
                if key not in self.entries.keys(): # check that there are no unwanted additions to JSON
                    self.messageprint("There is an unrecognized key in the JSON file.\n")
                    return
                # clear what's present
                if (key == "Wire") or (key == "Event") or (key == "WS Mode"):
                    self.entries[key].set('')
                else:
                    self.entries[key].delete(0,tk.END)
                # replace with set value
                if (tempinput[key] == "") or (tempinput[key] == []): 
                    pass
                else: 
                    errorcheck = self.checkentriescorrect({key: tempinput[key]}) # a check that the value is compatible
                    if errorcheck != False: 
                        if (key == "Wire") or (key == "Event") or (key == "WS Mode"): # comboboxes
                            self.entries[key].set(tempinput[key])
                        else: # entries
                            self.entries[key].insert(0,tempinput[key])
                    else: 
                        if (key == "Steps"): 
                            self.entries[key].insert(0,"12700")
                            self.messageprint(key+" has been restored to default.\n")
                        elif (key == "WS Mode"): 
                            self.entries[key].set("constant")
                            self.messageprint(key+" has been restored to default.\n")

            wire = self.entries["Wire"].get().strip()
            if wire in list(basicdata.pdict.keys()): # if a wire was selected with the json input
                self.readbackpopup(wire,frame122)
                self.plotinit(wire,frame21)
                if "Out Limit" not in cinkeys: 
                    self.changelims("Out Limit",wire)
                if "In Limit" not in cinkeys: 
                    self.changelims("In Limit",wire)
            return

    def lockentries(self,statestr,entrykeys,buttonkeys): 
        """Enable and disable buttons and entry widgets in the Tkinter GUI."""
        for entry in entrykeys: 
            self.entries[entry].config(state=statestr)
        for button in buttonkeys: 
            self.buttons[button].config(state=statestr)

    def startbutton(self,frame14): 
        self.lockentries("disabled",basicdata.lockedentries,basicdata.lockedbuttons) # locking to modification
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
        # check that the wire is in an ok position
        temppos = float(self.readbacks[basicdata.pdict[self.setpout["Wire"]][0]].get())
        if temppos <= self.setpout["Out Limit"]: 
            self.setpout["Direction"] = 0 # 0 for going in, 1 for going out
        elif temppos >= self.setpout["In Limit"]: 
            self.setpout["Direction"] = 1
        else: 
            self.messageprint(basicdata.pdict[self.setpout["Wire"]][0]+" is not outside In/Out Limit.\n")
            self.lockentries("enabled",basicdata.lockedentries,basicdata.lockedbuttons)
            return
        # add new frame with additional readbacks
        self.addparampopup(frame14,self.setpout["Additional Parameters"])              
        
        # things that doesn't need to be saved in setup parameters (some still are) but needs to be accessible by scan
        self.setpout["Timestamp"] = round(time.time()) # choose unix time stamp around now 
        # make directory
        savepath = os.path.join(self.setpout["Save Directory"],str(self.setpout["Timestamp"])+"_"+self.setpout["Wire"]).replace("\\","/")
        if not os.path.exists(savepath): 
            os.makedirs(savepath)
            self.setpout["WS Directory"] = savepath
        else: 
            self.messageprint("Folder for data unable to be created.\n")
            self.lockentries("enabled",basicdata.lockedentries,basicdata.lockedbuttons)
            return
        basicfuncs.dicttojson(self.setpout,os.path.join(self.setpout["WS Directory"],"_".join([str(self.setpout["Timestamp"]),self.setpout["Wire"],"SetupParameters.json"])))
        # make dict of tags
        tagdict, i = {}, 1
        for device in basicdata.pdict[self.setpout['Wire']]+basicdata.sdict[self.setpout['Wire']]+self.setpout['Additional Parameters']:
            tagdict[i]=device
            i=i+1
        self.setpout["Tags"] = tagdict

        # collect metadata 
        self.metad = {key:self.setpout[key] for key in ['Event', 'User Comment','Timestamp','WS Directory','Direction','Tags']}
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
        basicfuncs.dicttojson(self.metad,os.path.join(self.setpout["WS Directory"],"_".join([str(self.setpout["Timestamp"]),self.setpout["Wire"],",Metadata.json"])))
        
        # start wirescan 
        self.plot_thread = "liveplot" 
        self.acsyscontrol.start_scan_thread(self.scan_thread,self.setpout,self.lockentries,self.messageprint,self.plot_thread)
        self.messageprint("Scan initiated.\n")
        # start plotting here
        if self.plot_thread in self.acsyscontrol.get_list_of_threads(): 
            self.acsyscontrol.end_any_thread(self.plot_thread)
        print("Starting liveplot")
        self.acsyscontrol.start_liveplot_thread(self.plot_thread,self.scan_thread,self.setpout["Wire"],self.plotobjects)

    def abortbutton(self): 
        try: 
            if self.scan_thread in self.acsyscontrol.get_list_of_threads(): # kill existing thread if present
                self.acsyscontrol.end_any_thread(self.scan_thread)
                self.messageprint("Scan aborted by user.\n") 
                self.wiresout() # think more about this
            else: 
                self.messageprint("No scan to abort.\n")
        except AttributeError: 
            self.messageprint("No scan to abort.\n") 

    def wiresout(self):
        if self.entries["Wire"].get().strip() in basicdata.pdict.keys():
            self.acsyscontrol.setparam(basicdata.pdict[self.entries["Wire"].get().strip()][0],-12700)
            self.messageprint("Out setting issued to "+basicdata.pdict[self.entries["Wire"].get().strip()][0]+".\n")
        else: 
            self.messageprint("No wire selected, cannot pull wire out.\n")
        
class Adv_Window(tk.Toplevel): 
    def __init__(self,master):
        tk.Toplevel.__init__(self,master)
        self.title("Advanced Settings")
        self.protocol('WM_DELETE_WINDOW', self.done_adv)

        self.create_widgets_in_advwindow(master) 

    def create_widgets_in_advwindow(self,master):
        # setup frame
        frameA = ttk.LabelFrame(self,borderwidth=5,relief="solid",labelanchor="nw",text="Advanced Settings")
        frameA.grid(column=0,row=0,columnspan=1,pady=1,sticky="new")

        # setup contents
        textA = ["Additional Parameters","Steps","User Comment","WS Mode","Monitors","Monitor Min","Monitor Max"]
        for i, text in enumerate(textA):
            label = ttk.Label(frameA, text=text)
            label.grid(column=0, row=i, sticky='w', padx=5, pady=5)
            ToolTip(label,basicdata.tooltips[text])
        entryA1 = ttk.Entry(frameA)
        master.entries[textA[0]] = entryA1
        entryA1.grid(column=1, row=0, sticky='e', padx=5, pady=2)
        entryA2 = ttk.Entry(frameA)
        master.entries[textA[1]] = entryA2
        entryA2.insert(0,"12700")
        entryA2.grid(column=1, row=1, sticky='e', padx=5, pady=2)
        entryA3 = ttk.Entry(frameA)
        master.entries[textA[2]] = entryA3
        entryA3.grid(column=1, row=2, sticky='e', padx=5, pady=2)
        comboA4 = ttk.Combobox(frameA,state="readonly",values=basicdata.wsmodes,width=17)
        master.entries[textA[3]] = comboA4
        comboA4.set("constant")
        comboA4.grid(column=1, row=3, sticky='s', padx=2, pady=2)
        entryA5 = ttk.Entry(frameA)
        master.entries[textA[4]] = entryA5
        entryA5.grid(column=1, row=4, sticky='e', padx=5, pady=2)
        entryA6 = ttk.Entry(frameA)
        master.entries[textA[5]] = entryA6
        entryA6.grid(column=1, row=5, sticky='e', padx=5, pady=2)
        entryA7 = ttk.Entry(frameA)
        master.entries[textA[6]] = entryA7
        entryA7.grid(column=1, row=6, sticky='e', padx=5, pady=2)

    def done_adv(self): 
        self.grab_release() # release focus before withdrawing
        self.withdraw()

class ToolTip(): 
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