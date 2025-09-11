import json
import csv
import datetime
import numpy as np
import itertools
import basicdata

def checktype(value,type):
    """Check the type of a value: int, float, string, etc."""
    if type == int: 
        try: 
            f = float(value)
            if f.is_integer() is True: 
                i = int(value) 
                return True, i
            else: 
                return False, value
        except: 
            return False, value
    elif type == float: 
        try: 
            f = float(value)
            return True, f
        except: 
            return False, value 
    else: # strings and list
        return isinstance(value,type), value

def strtonum(value): 
    f = float(value)
    if f.is_integer() is True: 
        f = int(value) 
    return f

def dicttojson(indict,jsonstr): 
    """Save dict as a json."""
    outdict = indict.copy()
    for item in ["Additional Parameters", "Monitors", "Monitor Min", "Monitor Max"]: 
        if item in list(outdict.keys()): 
            outdict[item] = ", ".join([str(i) for i in outdict[item]])
    if jsonstr[-5:] != ".json": 
        jsonstr += ".json"
    with open(jsonstr,"w") as outfile: 
        json.dump(outdict,outfile)

def dicttocsv(indict,csvstr): 
    """Save dict as a csv."""
    if csvstr[-4:] != ".csv": 
        csvstr +=".csv"
    with open(csvstr,"w",newline='') as f: # NOTE: the newline thing is because of windows & Python3. probably take out for non windows?
        csvw = csv.writer(f)
        csvw.writerow(indict.keys())
        csvw.writerows(itertools.zip_longest(*indict.values())) # zip would crop to the shortest list in the dict, using itertools instead
    f.close()
    return 

def csvtodict(csvstr): 
    """Import a csv as a dict."""
    def convert(st): 
        try:
            if ((len(st) > 0) and (st[0] == "[")): # list 
                li = st.strip('][').split(', ') 
                for i in range(len(li)): 
                    li[i] = convert(li[i]) # recursively processing list
                return li
            else:
                f = float(st) # float
                if f%1 == 0:
                    return int(f) # int
                return f
        except ValueError:
            if st == "nan": # string
                return np.nan
            return st

    reader = csv.DictReader(open(csvstr))
    outdict = {}
    firstrow = 0
    for row in reader: 
        if firstrow == 0: # initialize lists
            for item in list(row.keys()): 
                outdict[item]=[]
            firstrow += 1
        for item in list(row.keys()): # add to list 
            num = convert(row[item]) 
            outdict[item] += [num]    
    return outdict

def rawtowires(indict,modstr): 
    """Convert raw format data from acsys into a dict with keys for each wire."""
    def checklengths(): 
        """Do a check that each wire has the same amount of data for that time, or fill in the gaps."""
        keylens = []
        for key in keylist: 
            keylens.append(len(outdict[key]))
        if max(keylens) - min(keylens) == 1: 
            # execute corrective action
            for j,length in enumerate(keylens): 
                if length < max(keylens): 
                    outdict[keylist[j]].append(np.nan)
        elif max(keylens) - min(keylens) > 1: 
            print("Something unexpected occurred. Please look at the data individually.")

    outdict = {}
    tagdict = {}
    j = 1
    keylist = basicdata.pdict[modstr]+basicdata.sdict[modstr]
    for key in keylist: # this assumes that we use the same pattern, which is fine
        outdict[key] = []
        tagdict[j] = key
        j=j+1
    
    currentstamp = 0
    for rownum in range(len(indict["tags"])): 
        # we check as to whether we've moved to a new time
        if indict['stamps'][rownum] != currentstamp: 
            currentstamp = indict['stamps'][rownum]
            # check that all the data are the same length, for the ones that aren't, append np.Nan
            checklengths()
        if indict["tags"][rownum] in tagdict.keys():
            outdict[tagdict[indict["tags"][rownum]]].append(indict["data"][rownum])
    checklengths() # need to call again to check that the last set rounded off right.
    return outdict

def caldatainterp(caldata,query,VorP):
    """Provide dictionary caldata (keys "Voltage" and "Phase" with lists inside) and a voltage as a query.""" 
    if VorP == "V": 
        sequence = ["Voltage","Phase",]
    elif VorP == "P": 
        sequence = ["Phase","Voltage",]
    else: 
        print("Please specify if the provided value is a Voltage or Phase.")
    for i,val in enumerate(caldata[sequence[0]]): 
        currsub = query-val
        if currsub == 0: 
            return caldata[sequence[1]][i]
        elif currsub < 0:  
            # execute linear interpolation 
            x1,x2,y1,y2 = caldata[sequence[0]][i-1], caldata[sequence[0]][i], caldata[sequence[1]][i-1], caldata[sequence[1]][i]
            return y1+(y2-y1)/(x2-x1)*(query-x1) # the equation is not the same for phase & voltage! it gets flipped! 

def bldproc(indict,maindict):
    # indict {"settings": [], 1: [[]], 2: [[]],}
    outdict = {} # in future, use caldata here

    # parse csv with caldata outside of interpolation calc, since we only want to do this once
    caldata = {"Voltage": [], "Phase": []}
    with open("caldata.csv") as file: 
        data = file.readlines()
    for i,line in enumerate(data): 
        if i == 0: continue 
        sline = line.split(",")
        caldata["Voltage"].append(float(sline[0].strip()))
        caldata["Phase"].append(float(sline[1].strip()))
    outdict[basicdata.pdict[maindict["BLD"]][0]] = [caldatainterp(caldata,x,"V") for x in indict["setting"]] # interpolated position data

    reading = basicdata.sdict[maindict["BLD"]]
    for key in maindict["Tags"]: 
        if maindict["Tags"][key] == reading:
            readingtag = key

    print(readingtag)
    print(list(indict.keys()))

    outdict[reading] = [np.average(x) for x in indict[readingtag]]
    outdict[reading+" Err"] = [np.std(x) for x in indict[readingtag]]

    return outdict

def avgtag(indict,tagkey): 
    """."""
    data = []

    for i, tag in enumerate(indict["tags"]): 
        if str(tag) == str(tagkey): 
            data.append(indict["data"][i]) 

    if len(data) >= 1: 
        avg = sum(data)/len(data)
        length = len(data)
        std = np.std(np.array(data))
        return avg, std, length
    else: 
        return False,False,False


if __name__ == "__main__":
    checktype()