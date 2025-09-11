import matplotlib.pyplot as plt

with open ("caldata.csv") as file: 
    data = file.readlines()

voltageD01 = []
phaseD01 = []
for i,line in enumerate(data):
    if i == 0: 
        continue
    vals = line.split(",")
    voltageD01.append(float(vals[0].strip())*2)
    phaseD01.append(float(vals[1].strip()))

# setup color,font,marker stuff
markers = ['o','v','s','>']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams["mathtext.fontset"] = 'dejavusans'

fig = plt.figure(1,(6,4))
plt.scatter(voltageD01,phaseD01,color="red",label="805 MHz")
plt.xlabel("Voltage (V)", fontweight="bold", fontsize=14)
plt.ylabel("Phase (Deg @ 805 MHz)", fontweight="bold", fontsize=14)
plt.xlim([0,20])
plt.ylim([0,360])
plt.legend(loc="best")
plt.grid()
fig.tight_layout()
plt.show()