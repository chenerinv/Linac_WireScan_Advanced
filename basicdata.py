pdict = { # RF position
    "D01": ["L:D01PHS"],
    "D03": ["L:D03PHS"], 
}
sdict = { # signal device
    "D01": ["L:D01BDS"],
    "D03": ["L:D03BDS"],
}
allparams = {
    "D01": ["L:D01PHS", "L:D01BDS", "L:D01BDM", "L:D01WHV", "L:D01HV1", "L:D01HV2", "L:62FT07", "L:D01WHI", "L:D01HI1", "L:D01HI2", "L:C0PHAS", "L:L0PADJ", "L:CVPHAS","L:LVPADJ","L:V5SQ","L:V5QSET",],
    "D03": ["L:D03PHS", "L:D03BDS", "L:D03BDM", "L:D03WHV", "L:D03HV1", "L:D03HV2", "L:62FT07", "L:D03WHI", "L:D03HI1", "L:D03HI2", "L:C0PHAS", "L:L0PADJ", "L:CVPHAS","L:LVPADJ","L:V5SQ","L:V5QSET",],
}

unitlist = ["deg", "V", "mm", "kV", "kV", "kV", "us", "mA", "mA", "mA", "deg", "deg", "deg", "deg","deg","deg"]

outlimdict = {"D01": 0,
              "D03": 0}
inlimdict = {"D01": 360,
             "D03": 360}
ylims = {"D01": [-0.1,5],
         "D03": [-0.1,5]} 

tooltips = {
    "Setup Parameters": "Optional. A quick way to set up a scan. Press Upload to load it in over current inputs.",
    "BLD": "Required. Select a wire scanner, called by its unique name.", 
    "Out Limit": "Required. Position (mm) where the wire is considered pulled out.",
    "In Limit": "Required. Position (mm) where the wire is fully in.", 
    "Event": "Required. Event to collect data on.",
    "Save Directory": "Required. Directory to save data from scan.",
    "Additional Parameters": "Optional. Separate AcNet parameters with commas for parameters to be recorded. Only first 8 will show in GUI, but all will be recorded.",
    "Steps": "Required. Number of steps to issue in AcSys as setting for constant speed scan. Default 12700.",
    "User Comment": "Optional. Insert any comments to include in the metadata.",
    "WS Mode": "[Not functional]. Required. Modes of WS motion control.",
    "Monitors": "[Not functional] Separate AcNet parameters with commas to monitor these devices.",
    "Monitor Min": "[Not functional] Minimum values for the monitors, separated by comma and indexed matching 'Monitors.'",
    "Monitor Max": "[Not functional] Maximum values for the monitors, separated by comma and indexed matching 'Monitors.'",
    "xlim": "Optional. Set a fixed range for plot export. Input a range separated by a comma, e.g. 20, 50",
    "ylim": "Optional. Set a fixed range for plot export. Input a range separated by a comma, e.g. 20, 50",
    "Settings Enabled": "Check to reveal the options for configuring a scan. Leave unchecked to only collect, not set.",
    "Center Phase": "Value (deg) the range should center around.",
    "Phase Step": "Step (deg) in phase of the measurement.",
    "Half-Range": "Range of half the scan in degrees. May be slightly over if step does not match correctly.",
    "Samples Per Point": "Number of samples to take on event at each phase.",
}

helpstrings = {
    1: "- Hover over a label for more information about that entry.\n- Line 2",
    2: ("    The Setup Parameters is meant to act as a quick method for intializing a wire scan, especially during studies "
        "so wire scans can be configured beforehand. There are three valid 'cases' of Setup Parameters parameter use: \n"
        "    1: Including a parameter with a valid value will override what is displayed in the GUI. \n"
        "    2: The exclusion of a parameter from the Setup Parameters will lead to this parameter not being cleared or "
        "updated if already selected in the GUI. \n    3: Including a parameter in the Configuration "
        "Input with a value of an empty string or empty list will clear that parameter from the GUI and leave it blank (even "
        "In Limit and Out Limit, which typically auto-update upon wire selection). The exception to this clearing functionality "
        "are the dropdown lists for Wire, Event, and WS Mode, which are required parameters and if selected in the GUI prior to "
        "upload, will not clear. \n    In the case of an invalid entry, the parameter will clear unless it is Steps or WS Mode, "
        "which will restore to default. \n\n    Configuration inputs are case sensitive."),
    3: "Version 0, updated 3/15/2023 \nContact Erin Chen erinchen@fnal.gov about comments, questions, & concerns.",
    4: "An example Setup Parameters is shown below: "
}

events = ["0A","0C","17","00","1D","52"]

wsmodes = ["constant","steps"]

plots = ["Plot1","Plot2","Plot3"]
colorlist1 = ['tab:blue','mediumpurple','yellowgreen','tab:cyan','royalblue','plum','darkkhaki','skyblue']
colorlist2 = ['red','darkorange','gold','hotpink','red','darkorange','gold','hotpink','red','darkorange','gold','hotpink']
markerlinelist = ['-',':','-.','--','o-','v-','^-','s-','o:','v:','^:','s:']

checkcorrect = {
    "BLD": str,
    "Out Limit": float,
    "In Limit": float,
    "Event": str,
    "Additional Parameters": str,
    "Steps": int,
    "User Comment": str,
    "WS Mode": str,
    "Monitors": str,
    "Monitor Min": str,
    "Monitor Max": str,
    "Save Directory": str,
    "xlim": str,
    "ylim": str,
    "Settings Enabled": int,
    "Center Phase": float,
    "Phase Step": float,
    "Half-Range": float,
    "Samples Per Point": int,
}

requiredkeys = ["BLD", "Event", "Save Directory"]
skippedkeys = ["Messages", "Setup Parameters", "Help1", "Help2", "Help3","Browse1","Upload","Browse2","Start","Stop"]
ignorekeys = ["Timestamp","BLD Directory","Direction","Source","L:D7TOR","Pulse Length", "Frequency","Tags"]
lockedentries = ["BLD","Event","Save Directory","User Comment","Additional Parameters","xlim","ylim",
                 "Center Phase","Phase Step","Half-Range","Samples Per Point","Browse1", "Upload", "Browse2","Start","Settings Enabled"]