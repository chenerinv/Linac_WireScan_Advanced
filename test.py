import matplotlib.pyplot as plt
import numpy as np

x = [1,2,3,4,5,6,7,8,9,]
y = [1,2,3,4,5,6,7,8,9,]

props = dict(boxstyle='round', facecolor='white', alpha=0.8)

pcov = np.array([[1,3,3,2],[3,4,2,1],[1,2,3,1],[3,2,3,2]])
x0 = 0.1
sigma = 3
FWHM = 12.4
ps = 10

textstr = '\n'.join((
    r'$\mu=%.2f\pm%.2f$' % (x0, np.sqrt(pcov[2][2]),),
    r'$\sigma=%.2f\pm%.2f$' % (sigma, np.sqrt(pcov[3][3]),),
    r'$\mathrm{FWHM}=%.2f\mathrm{ps}$' % (ps, )))

plt.figure()
ax = plt.axes()

plt.plot(x,y)

ax.text(0.75, 0.95, textstr, color='k', fontsize='medium', verticalalignment='top', bbox=props,transform=ax.transAxes)

plt.show()