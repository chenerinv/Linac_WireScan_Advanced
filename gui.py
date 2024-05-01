import tkinter as tk
from tkinter import ttk, filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math
import os
import json
import time

import basicdata
import basicfuncs
from acsyscontrol import acsyscontrol 

class WireScanApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Constant Speed Wire Scan App")
        self.geometry("850x365")
        self.minsize(850,365)
        self.entries = {} # tk entries
        self.buttons = {} # tk buttons
        self.setpout = {} # dictionary with setup data
        self.metad = {} # dictionary with metadata
        self.readbacks = {} # dictionary for live readbacks
        self.pastreadbacks = {1:[], 2:[]} # reference info for killing and restarting a plot
        self.plotobjects = {"Frame":{},"Canvas":{},"Fig":{},"Ax":{},"ScatterObj":{}} # matplotlib objects
        self.acsyscontrol = acsyscontrol()

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
        self.tab2.columnconfigure(0,weight=0,minsize=480)
        self.tab2.columnconfigure(1,weight=1)
        self.tab2.rowconfigure(3,weight=1)

        # Create Tab3
        self.tab3 = ttk.Frame(self.tabControl)
        self.tabControl.add(self.tab3, text='Help')
        self.tab3.columnconfigure(0,weight=1,minsize=425)
        self.tab3.columnconfigure(1,weight=1,minsize=425)

        # Create Advanced Parameters Window (hidden until opened)
        self.AdvChild = Adv_Window(self)
        self.AdvChild.withdraw()

        # Add widgets to Tab1
        self.create_widgets_in_tab1()
        self.create_widgets_in_tab3()
        self.bind_all('<Button>', self.change_focus)
    
    def create_widgets_in_tab1(self): 
        # create subframes in tab1
        frame00 = ttk.LabelFrame(self.tab1,borderwidth=5,relief="solid",labelanchor="nw",text="Quick Setup")
        frame00.grid(column=0,row=0,columnspan=1,pady=1,sticky="nw")
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
        text1 = tk.Text(frame04,height = 4,width=56,state="disabled",yscrollcommand=s1.set,wrap=tk.WORD)
        text1.pack(side=tk.LEFT,fill=tk.Y)
        self.entries["Messages"] = text1
        s1.config(command=text1.yview)

        # frame01
        frame010 = ttk.LabelFrame(frame01,borderwidth=5,relief="solid",labelanchor="nw",text="Wire")
        frame010.grid(column=0,row=0,columnspan=1,pady=1,sticky="w")
        frame011 = ttk.LabelFrame(frame01,borderwidth=5,relief="solid",labelanchor="nw",text="Readbacks")
        frame011.grid(column=1,row=0,columnspan=1,pady=1,sticky="e") # nested in frame 01, so must be made here not readbackpopup()

        # frame00
        text00 = "Setup Parameters"
        label00 = ttk.Label(frame00, text=text00)
        label00.grid(column=0, row=0, sticky='w', padx=5, pady=5)
        ToolTip(label00,basicdata.tooltips[text00])
        entry00 = ttk.Entry(frame00)
        entry00.grid(column=1, row=0, sticky='ew', padx=5, pady=2)
        self.entries[text00] = entry00
        browse_button_00 = ttk.Button(frame00, text='Browse', command=lambda e=entry00, t=text00: self.browse(e,t))
        browse_button_00.grid(column=2, row=0, padx=5, pady=2)
        self.buttons["Browse1"] = browse_button_00
        upload_button = ttk.Button(frame00, text='Upload', command=lambda: self.loadsetp(frame011,frame10)) #TODO remove & integrate into browse1
        upload_button.grid(column=3, row=0, sticky='e', padx=5, pady=2)
        self.buttons["Upload"] = upload_button

        # frame010
        labels = ["Wire","Out Limit","In Limit", "Event"]
        for i, text in enumerate(labels):
            label = ttk.Label(frame010, text=text)
            label.grid(column=i, row=0, sticky='n', padx=2, pady=2)
            ToolTip(label,basicdata.tooltips[text])
        entry010_0 = ttk.Entry(frame010,width=8)
        entry010_0.grid(column=1, row=1, sticky='s', padx=2, pady=2)
        self.entries[labels[1]] = entry010_0
        entry010_1 = ttk.Entry(frame010,width=8)
        entry010_1.grid(column=2, row=1, sticky='s', padx=2, pady=2)
        self.entries[labels[2]] = entry010_1
        combo010_0 = ttk.Combobox(frame010,state="readonly",values=list(basicdata.pdict.keys()),width=4) 
        combo010_0.grid(column=0, row=1, sticky='s', padx=2, pady=2)
        combo010_0.bind("<<ComboboxSelected>>", lambda event: self.selectedwire(frame011,frame10))
        self.entries[labels[0]] = combo010_0
        combo010_1 = ttk.Combobox(frame010,state="readonly",values=basicdata.events,width=3)
        combo010_1.grid(column=3, row=1, sticky='s', padx=2, pady=2)
        self.entries[labels[3]] = combo010_1
        adv_button = ttk.Button(frame010, text="Advanced Settings", command=self.open_advwindow)
        adv_button.grid(column=0, row=2, columnspan=4, padx=1, pady=1)

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
        wout_button = ttk.Button(frame02, text="Wires Out", command=self.wiresout)
        wout_button.grid(column=1, row=1, columnspan=1, padx=1, pady=1)
        self.buttons["Wires Out"] = wout_button
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
        texth1 = tk.Text(frameh00,height=4,state="disabled",yscrollcommand=sh1.set,wrap=tk.WORD)
        texth1.pack(side=tk.LEFT,fill=tk.Y)
        self.entries["Help1"] = texth1
        self.messageprint(basicdata.helpstrings[1],texth1)
        sh1.config(command=texth1.yview)

        # frameh10
        sh2 = tk.Scrollbar(frameh10)
        sh2.pack(side=tk.RIGHT,fill=tk.Y)
        texth2 = tk.Text(frameh10,height=10,state="disabled",yscrollcommand=sh2.set,wrap=tk.WORD)
        texth2.pack(side=tk.LEFT,fill=tk.Y)
        self.entries["Help2"] = texth2
        self.messageprint(basicdata.helpstrings[2],texth2)
        sh2.config(command=texth2.yview)

        # frameh01
        sh3 = tk.Scrollbar(frameh01)
        sh3.pack(side=tk.RIGHT,fill=tk.Y)
        texth3 = tk.Text(frameh01,height=4,state="disabled",yscrollcommand=sh3.set,wrap=tk.WORD)
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

    def open_advwindow(self):
        """Open pop-up window with Advanced Parameters. Steals focus until window is closed."""
        self.AdvChild.deiconify()
        self.AdvChild.grab_set() # keep focus on advanced param window

    def browse(self, entry_widget, text):
        """Browse for a file."""
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
        """Automatically change the in/out limits based on selection of wire."""
        widget1 = self.entries[keywidget]
        widget1.delete(0, tk.END)
        if keywidget == "Out Limit": 
            widget1.insert(tk.END, basicdata.outlimdict[value])
        elif keywidget == "In Limit":
            widget1.insert(tk.END, basicdata.inlimdict[value])

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
        value = self.entries["Wire"].get().strip() # could have used event.widget.get() if we passed event through lambda
        self.changelims("Out Limit",value)
        self.changelims("In Limit",value)
        self.readbackpopup(value,frame011) #technically could get value in these, but it is easier to just pass it?
        self.plotinit(value,frame10)

    def plotinit(self,value,frame10): 
        '''Initializing axes of the live plot upon wire selection & deleting previous subplots.'''
        # deleting existing frames, canvas, figs        
        for widgets in frame10.winfo_children(): # delete eveyrthing in frame
            widgets.destroy()
        # resetting the dictionary of stuff
        self.plotobjects = {"Frame":{},"Canvas":{},"Fig":{},"Ax":{},"ScatterObj":{}}
        # building and saving all needed objects in plotobjects
        j = 0
        for i,key in enumerate(basicdata.pdict[value]): 
            self.plotobjects["Frame"][key] = ttk.Frame(frame10)
            self.plotobjects["Frame"][key].grid(column=0,row=j,columnspan=1,pady=1,sticky="we")
            frame10.rowconfigure(j,weight=1)
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
        frame10.columnconfigure(0,weight=1)

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
        pos, sig = basicdata.pdict[value], basicdata.sdict[value]
        for i, text in enumerate(pos):
            label = ttk.Label(frame011, text=text+":")
            label.grid(column=0, row=i, sticky='n', padx=0, pady=2)
            self.readbacks[text] = tk.StringVar()
            self.pastreadbacks[1].append(text)
            label1 = ttk.Label(frame011, textvariable=self.readbacks[text]) 
            label1.grid(column=1, row=i, sticky='n', padx=0, pady=2)
            label2 = ttk.Label(frame011, text=" mm")
            label2.grid(column=2, row=i, sticky='n', padx=2, pady=2)
        for i, text in enumerate(sig):
            label = ttk.Label(frame011, text=text+":")
            label.grid(column=3, row=i, sticky='n', padx=2, pady=2)
            self.readbacks[text] = tk.StringVar()
            self.pastreadbacks[1].append(text)
            label1 = ttk.Label(frame011, textvariable=self.readbacks[text]) 
            label1.grid(column=4, row=i, sticky='n', padx=0, pady=2)
            label2 = ttk.Label(frame011, text=" V")
            label2.grid(column=5, row=i, sticky='n', padx=0, pady=2)
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

    def loadsetp(self,frame011,frame10): 
        """Function for the Upload button. 
        Executes necessary actions to upload data from a JSON to the program & GUI. 
        Confirms entries are appropriate.
        """
        filepath = self.entries['Setup Parameters'].get().strip() # getting the data from the uploaded file.
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
            # start parsing the data
            for ignorekey in basicdata.ignorekeys: # skipping the additional keys in Setup Params
                if ignorekey in list(tempinput.keys()): 
                    del tempinput[ignorekey]
            cinkeys = list(tempinput.keys())
            # execute all of the checks
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
            # initate the actions that happen after Wire is selected
            wire = self.entries["Wire"].get().strip()
            if wire in list(basicdata.pdict.keys()): # if a wire was selected with the json input
                self.readbackpopup(wire,frame011)
                self.plotinit(wire,frame10)
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
        """Abort an ongoing scan."""
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
        """Issue setting to move wire to the out position."""
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
        entryA0 = ttk.Entry(frameA)
        master.entries[textA[0]] = entryA0
        entryA0.grid(column=1, row=0, sticky='e', padx=5, pady=2)
        entryA1 = ttk.Entry(frameA)
        master.entries[textA[1]] = entryA1
        entryA1.insert(0,"12700")
        entryA1.grid(column=1, row=1, sticky='e', padx=5, pady=2)
        entryA2 = ttk.Entry(frameA)
        master.entries[textA[2]] = entryA2
        entryA2.grid(column=1, row=2, sticky='e', padx=5, pady=2)
        comboA3 = ttk.Combobox(frameA,state="readonly",values=basicdata.wsmodes,width=17)
        master.entries[textA[3]] = comboA3
        comboA3.set("constant")
        comboA3.grid(column=1, row=3, sticky='s', padx=2, pady=2)
        entryA4 = ttk.Entry(frameA)
        master.entries[textA[4]] = entryA4
        entryA4.grid(column=1, row=4, sticky='e', padx=5, pady=2)
        entryA5 = ttk.Entry(frameA)
        master.entries[textA[5]] = entryA5
        entryA5.grid(column=1, row=5, sticky='e', padx=5, pady=2)
        entryA6 = ttk.Entry(frameA)
        master.entries[textA[6]] = entryA6
        entryA6.grid(column=1, row=6, sticky='e', padx=5, pady=2)

    def done_adv(self): 
        """Actions when window is complete."""
        self.grab_release() # release focus before withdrawing
        self.withdraw()

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