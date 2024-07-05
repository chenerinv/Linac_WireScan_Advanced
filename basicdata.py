pdict = {
    "D01": ["L:D01WPX","L:D01WPY","L:D01WPU"],
    "D02": ["L:D02WPX","L:D02WPY","L:D02WPU"],
    "D03": ["L:D03WPX","L:D03WPY","L:D03WPU"],
    "D12": ["L:D12WPX","L:D12WPY","L:D12WPU"],
    "D13": ["L:D13WPX","L:D13WPY","L:D13WPU"],
    "D23": ["L:D23WPX","L:D23WPY","L:D23WPU"],
    "D33": ["L:D33WPX","L:D33WPY","L:D33WPU"],
    "D43": ["L:D43WPX","L:D43WPY","L:D43WPU"],
    "D53": ["L:D53WPX","L:D53WPY","L:D53WPU"],
    "D63": ["L:D63WPX","L:D63WPY","L:D63WPU"],
    "D64": ["L:D64WPX","L:D64WPY","L:D64WPU"],
    "D73": ["L:D73WPX","L:D73WPY","L:D73WPU"],
    "D81": ["L:D81WPX","L:D81WPY","L:D81WPU"],
    "D83": ["L:D83WPX","L:D83WPY","L:D83WPU"],
    "DE1": ["L:DE1WPX","L:DE1WPY"],
    "DE3": ["L:DE3WPX","L:DE3WPY"]
}
sdict = {
    "D01": ["L:D01WSX","L:D01WSY","L:D01WSU"],
    "D02": ["L:D02WSX","L:D02WSY","L:D02WSU"],
    "D03": ["L:D03WSX","L:D03WSY","L:D03WSU"],
    "D12": ["L:D12WSX","L:D12WSY","L:D12WSU"],
    "D13": ["L:D13WSX","L:D13WSY","L:D13WSU"],
    "D23": ["L:D23WSX","L:D23WSY","L:D23WSU"],
    "D33": ["L:D33WSX","L:D33WSY","L:D33WSU"],
    "D43": ["L:D43WSX","L:D43WSY","L:D43WSU"],
    "D53": ["L:D53WSX","L:D53WSY","L:D53WSU"],
    "D63": ["L:D63WSX","L:D63WSY","L:D63WSU"],
    "D64": ["L:D64WSX","L:D64WSY","L:D64WSU"],
    "D73": ["L:D73WSX","L:D73WSY","L:D73WSU"],
    "D81": ["L:D81WSX","L:D81WSY","L:D81WSU"],
    "D83": ["L:D83WSX","L:D83WSY","L:D83WSU"],
    "DE1": ["L:DE1WSX","L:DE1WSY"], # ,"L:DE1WSU"
    "DE3": ["L:DE3WSX","L:DE3WSY"] # ,"L:DE3WSU"
}
outlimdict = {"D01": -40, "D02": -40, "D03": -40, "D12": -40, "D13": -40, "D23": -40, "D33": -40, "D43": -40, 
    "D53": -40, "D63": -40, "D64": -40, "D73": -40, "D81": -15, "D83": -20, "DE1": -25, "DE3": -25}
inlimdict = {"D01": 14, "D02": 14, "D03": 14, "D12": 14, "D13": 14, "D23": 14, "D33": 14, "D43": 14,
    "D53": 14, "D63": 14, "D64": 14, "D73": 14, "D81": 40, "D83": 45, "DE1": 45, "DE3": 30}
ylims = {"D01": [-1,0.1], "D02": [-1,0.1], "D03": [-1,0.1], "D12": [-1,0.1], "D13": [-1,0.1], "D23": [-1,0.1], "D33": [-1,0.1], "D43": [-1,0.1], 
    "D53": [-1,0.1], "D63": [-1,0.1], "D64": [-1,0.1], "D73": [-1,0.1], "D81": [-1,0.1], "D83": [-1,0.1], "DE1": [-1,0.1], "DE3": [-1,0.1]} 
# update to real values

tooltips = {
    "Setup Parameters": "Optional. A quick way to set up a scan. Press Upload to load it in over current inputs.",
    "Wire": "Required. Select a wire scanner, called by its unique name.", 
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
    "Monitor Max": "[Not functional] Maximum values for the monitors, separated by comma and indexed matching 'Monitors.'"
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

events = ["0A","0C","17","00"]

wsmodes = ["constant","steps"]

plots = ["Plot1","Plot2","Plot3"]
colorlist1 = ['tab:blue','mediumpurple','yellowgreen','tab:cyan','royalblue','plum','darkkhaki','skyblue']
colorlist2 = ['red','darkorange','gold','hotpink','red','darkorange','gold','hotpink','red','darkorange','gold','hotpink']
markerlinelist = ['-',':','-.','--','o-','v-','^-','s-','o:','v:','^:','s:']

checkcorrect = {
    "Wire": str,
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
    "Save Directory": str
}

requiredkeys = ["Wire", "Out Limit", "In Limit", "Event", "Steps", "Save Directory"]
skippedkeys = ["Messages", "Setup Parameters", "Help1", "Help2", "Help3"]
ignorekeys = ["Timestamp","WS Directory","Direction","Source","L:D7TOR","Pulse Length", "Frequency","Tags"]
lockedentries = ["Wire","Out Limit","In Limit", "Event", "Steps", "Save Directory","Setup Parameters","Monitors", "Monitor Min", "Monitor Max", "WS Mode","User Comment","Additional Parameters"]
lockedbuttons = ["Browse1","Upload","Browse2","Start"] #,"Wires Out"


qlist = ["G:AMANDA","L:Q01", "L:Q02", "L:Q03", "L:Q04", "L:Q11", "L:Q12", "L:Q13", "L:Q14", "L:Q21", "L:Q22", "L:Q23", "L:Q24", 
         "L:Q31", "L:Q32", "L:Q33", "L:Q34", "L:Q41", "L:Q42", "L:Q43", "L:Q44", "L:Q51", "L:Q52", "L:Q53", "L:Q54", 
         "L:Q61", "L:Q62", "L:Q63", "L:Q64", "L:Q71", "L:Q72", "L:Q73", "L:Q74"]