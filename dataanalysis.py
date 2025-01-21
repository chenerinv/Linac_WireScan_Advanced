import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit as cf
import basicdata
import basicfuncs
import os
from scipy.signal import find_peaks, peak_widths
from scipy.optimize import curve_fit
from functools import reduce
import pandas as pd
import scipy.integrate as integrate

class dataanalysis: 
    def __init__(self): 
        self.temp = []
    
    def gauss(x, H, A, x0, sigma):
        #return 0.75 + A * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))
        return H + A * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))

    def gauss_fit(x, y, e):
        mean = sum(x * y) / sum(y)
        sigma = np.sqrt(sum(y * (x - mean) ** 2) / sum(y))
        popt, pcov = curve_fit(gauss, x, y, p0=[min(y), max(y), mean, sigma], sigma=e, absolute_sigma=True)

        return popt,pcov

    # summary of fit methods
    def endscanproc(self,procdata,coutput): 
        for i in range(len(basicdata.pdict[coutput["BLD"]])): 
            fitstats= {}
            
            x = basicdata.pdict[coutput["BLD"]][i]
            y = basicdata.sdict[coutput["BLD"]][i]

            # sorting lists to have data points in order of x 
            ysorted = [x for _,x in sorted(zip(procdata[x],procdata[y]))] # sorting y based on x
            xsorted = sorted(procdata[x])
            
            # converting to pandas dataframe for Ralitsa's FWHM peakfinding code
            t_df = pd.DataFrame({x: xsorted, y: ysorted})
            try: 
                peaks, _ = find_peaks(t_df['L:D03BDS'],prominence=0.15) #TODO change to 0.9 for real mode
                widths, heights, left_ips, right_ips = peak_widths(t_df['L:D03BDS'], peaks, rel_height=0.6)
                fwhm = t_df['L:DDMOT3'].iloc[round(right_ips[0])]- t_df['L:DDMOT3'].iloc[round(left_ips[0])]

                fitstats["FWHM"] = fwhm
                fitstats["peaks"] = peaks
                fitstats["widths"] = widths
                fitstats["heights"] = heights
                fitstats["left_ips"] = left_ips
                fitstats["right_ips"] = right_ips
            except: 
                fitstats["FWHM"] = None
                fitstats["peaks"] = None
                fitstats["widths"] = None
                fitstats["heights"] = None
                fitstats["left_ips"] = None
                fitstats["right_ips"] = None

            # # gaussian fitting & basic plotting
            # rms = np.std(t_df['L:D03BDS'].iloc[:10])
            # x0 = np.zeros(len(t_df))
            # sigma = np.zeros(len(t_df))
            # x0err = np.zeros(len(t_df))
            # sigmaerr = np.zeros(len(t_df))
            # integral = np.zeros(len(t_df))
            # A = np.zeros(len(t_df))
            # c0phas = [np.round(t['L:C0PHAS'].mean()) for t in t_df]

            # fig2,axs = plt.figure(figsize=(8,6))
            # props = dict(boxstyle='round', facecolor='white', alpha=0.8)

            # for j in range(len(t_df)):
            #     errors = np.ones(len(t_df[j]['L:D03BDS']))*rms
            #     (H, A[j], x0[j], sigma[j]),pcov = gauss_fit(t_df[j]['L:DDMOT3'], t_df[j]['L:D03BDS'], errors)
            #     FWHM = 2.35482 * sigma[j]
            #     ps = 1./201.5e6 * FWHM/360. * 1e12
            #     #integral[j] = integrate.cumulative_trapezoid(gauss(t_df[j]['L:DDMOT3'],H,A[j],x0[j],sigma[j]),t_df[j]['L:DDMOT3'])[-1]
            #     integral[j] = A[j]*sigma[j]*np.sqrt(2*np.pi)
            #     print(FWHM, abs(integral[j]))
                
            #     x0err[j] = np.sqrt(pcov[2][2])
            #     sigmaerr[j] = np.sqrt(pcov[3][3])
            #     textstr = '\n'.join((
            #             r'$\mu=%.2f\pm%.2f$' % (x0[j], np.sqrt(pcov[2][2]),),
            #             r'$\sigma=%.2f\pm%.2f$' % (sigma[j], np.sqrt(pcov[3][3]),),
            #             r'$\mathrm{FWHM}=%.2f\mathrm{ps}$' % (ps, )))

            #     axs[int(j%(len(t_df)/2))][int(j/(len(t_df)/2))].plot(t_df[j]['L:DDMOT3'], t_df[j]['L:D03BDS'], '.',color='k', label='%s'%c0phas[j])
            #     axs[int(j%(len(t_df)/2))][int(j/(len(t_df)/2))].plot(t_df[j]['L:DDMOT3'], gauss(t_df[j]['L:DDMOT3'], *gauss_fit(t_df[j]['L:DDMOT3'], 
            #                 t_df[j]['L:D03BDS'], errors)[0]), '-',color='r', label='fit')
            #     axs[int(j%(len(t_df)/2))][int(j/(len(t_df)/2))].grid(True)
            #     axs[int(j%(len(t_df)/2))][int(j/(len(t_df)/2))].legend()
            #     axs[int(j%(len(t_df)/2))][int(j/(len(t_df)/2))].text(0.65, 0.95, textstr, transform=axs[int(j%(len(t_df)/2))][int(j/(len(t_df)/2))].transAxes, color='k', fontsize='medium',
            #                         verticalalignment='top', bbox=props)

            # fig2.supylabel('EMT signal (V)',fontsize='x-large')
            # fig2.supxlabel('Trombone phase (deg@201 MHz)',fontsize='x-large')
            # plt.subplots_adjust(wspace=0, hspace=0)
            # plt.subplots_adjust(bottom=0.09)
            # plt.subplots_adjust(top=0.95)
            # plt.subplots_adjust(left=0.10)
            # plt.subplots_adjust(right=0.98)
            # plt.show()        


            # fitstats = self.gaussfit(x,y,procdata[x],procdata[y])
            # basicfuncs.dicttojson(fitstats,os.path.join(coutput["BLD Directory"],"_".join([str(coutput["Timestamp"]),coutput["BLD"],x[-1].upper(),"GaussianFitStats.json"])))
            # # make standard plots based on data, save as png.
            # if fitstats["error"] == None: 
            #     try: 
            #         matplotlib.use('agg')
            #         plt.figure()
            #         plt.scatter(procdata[x],procdata[y],label="BLD Data")
            #         xtemp = np.linspace(min(procdata[x]),max(procdata[x]),1000)
            #         plt.plot(xtemp,[self.gauss(x,fitstats['amp'],fitstats['peak'],fitstats['sigma'],fitstats['float']) for x in xtemp],color='red',label="Gaussian Fit")
            #         plt.xlabel("Trombone phase (deg@201 MHz)")
            #         plt.ylabel("EMT signal (V)")
            #         plt.title(", ".join([coutput["Wire"],x[-1].upper()]))
            #         plt.legend()
            #         plt.savefig(os.path.join(coutput["BLD Directory"],"_".join([str(coutput["Timestamp"]),coutput["BLD"],x[-1].upper(),"Plot.png"])))
            #         plt.close()
            #     except: 
            #         print("Plotting failed!")

    # return list of data corresponding to the input parameters and dataset
    def generatefitline(self,inputnp,params,fit): 
        if fit == "gauss": 
            return [self.gauss(x,params['amp'],params['peak'],params['sigma'],params['float']) for x in inputnp]