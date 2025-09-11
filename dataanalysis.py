import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import basicdata
import basicfuncs
import os
from scipy.signal import find_peaks, peak_widths
from scipy.optimize import curve_fit
import pandas as pd

class dataanalysis: 
    def __init__(self): 
        self.temp = []

    # summary of fit methods
    def endscanproc(self,procdata,coutput,xlim=[None,None],ylim=[None,None]): 
        def gauss(x, H, A, x0, sigma):
            #return 0.75 + A * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))
            return H + A * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))

        def gauss_fit(x, y, e):
            mean = sum(x * y) / sum(y)
            sigma = np.sqrt(sum(y * (x - mean) ** 2) / sum(y))
            popt, pcov = curve_fit(gauss, x, y, p0=[min(y), max(y), mean, sigma], sigma=e, absolute_sigma=True)
            return popt,pcov
        
        for i in range(len(basicdata.pdict[coutput["BLD"]])): 
            fitstats= {}
            
            x = basicdata.pdict[coutput["BLD"]][i]
            y = basicdata.sdict[coutput["BLD"]][i]

            if basicdata.sdict[coutput["BLD"]][i]+" Err" in list(procdata.keys()): 
                yerr = basicdata.sdict[coutput["BLD"]][i]+" Err"
                yerrsorted = [b for _,b in sorted(zip(procdata[x],procdata[yerr]))]

            # sorting lists to have data points in order of x 
            ysorted = [b for _,b in sorted(zip(procdata[x],procdata[y]))] # sorting y based on x
            xsorted = sorted(procdata[x])

            # temp for testing
            # xsorted = np.linspace(-50,50,200)
            # ysorted = np.multiply(np.array(gauss(xsorted,0,3,0,8)), np.array(np.random.normal(1,1.1,200)))
            # xsorted = xsorted.tolist()
            # ysorted = ysorted.tolist()

            # converting to pandas dataframe for Ralitsa's FWHM peakfinding code
            t_df = pd.DataFrame({x: xsorted, y: ysorted})
            try: 
                peaks, _ = find_peaks(t_df[y],prominence=0.9) #TODO change to 0.9 for real mode
                widths, heights, left_ips, right_ips = peak_widths(t_df[y], peaks, rel_height=0.6)
                fwhm = t_df[x].iloc[round(right_ips[0])]- t_df[x].iloc[round(left_ips[0])]

                fitstats["FWHM_raw"] = fwhm
                fitstats["peaks"] = peaks.tolist()
                fitstats["widths"] = widths.tolist()
                fitstats["heights"] = heights.tolist()
                fitstats["left_ips"] = left_ips.tolist()
                fitstats["right_ips"] = right_ips.tolist()
            except: 
                fitstats["FWHM_raw"] = None
                fitstats["peaks"] = None
                fitstats["widths"] = None
                fitstats["heights"] = None
                fitstats["left_ips"] = None
                fitstats["right_ips"] = None

            # gaussian fitting & basic plotting
            rms = np.std(t_df[y].iloc[:10])
            fitstats["rms"] = rms
            x0 = np.zeros(len(t_df))
            sigma = np.zeros(len(t_df))
            x0err = np.zeros(len(t_df))
            sigmaerr = np.zeros(len(t_df))
            integral = np.zeros(len(t_df))
            A = np.zeros(len(t_df))
        
            matplotlib.use('agg')
            plt.figure(figsize=(8,6))
            ax = plt.axes()
            props = dict(boxstyle='round', facecolor='white', alpha=0.8)
            try: 
                errors = np.ones(len(t_df[y]))*rms
                (H, A, x0, sigma),pcov = gauss_fit(t_df[x], t_df[y], errors)
                FWHM = 2.35482 * sigma
                ps = 1./201.5e6 * FWHM/360. * 1e12
                integral = A*sigma*np.sqrt(2*np.pi)
                x0err = np.sqrt(pcov[2][2])
                sigmaerr = np.sqrt(pcov[3][3])
                fitstats["FWHM_ps"] = ps
                fitstats["FWHM_Gauss"] = FWHM
                fitstats["GaussFit"] = [H,A,x0,sigma]
                fitstats["pcov"] = pcov.tolist()
                fitstats["x0err"] = x0err
                fitstats["sigmaerr"] = sigmaerr
                fitstats["integral"] = abs(integral)
                fitgaussgo = 1
            except: 
                fitstats["FWHM_ps"] = None
                fitstats["FWHM_Gauss"] = None
                fitstats["GaussFit"] = None
                fitstats["pcov"] = None
                fitstats["x0err"] = None
                fitstats["sigmaerr"] = None
                fitstats["integral"] = None
                fitgaussgo = 0

            basicfuncs.dicttojson(fitstats,os.path.join(coutput["BLD Directory"],"_".join([str(coutput["Timestamp"]),coutput["BLD"],"FitStats.json"])))
            
            if basicdata.sdict[coutput["BLD"]][i]+" Err" in list(procdata.keys()): 
                plt.errorbar(t_df[x], t_df[y], yerr=yerrsorted, marker='.',color='k', label='raw',ls='none',capsize=4)
            else: 
                plt.plot(t_df[x], t_df[y], '.',color='k', label='raw')
            plt.grid(True)
            plt.ylabel('EMT signal (V)',fontsize='x-large')
            plt.xlabel('Trombone phase (deg@805 MHz)',fontsize='x-large')
            if xlim != [None,None]: 
                plt.xlim(*xlim)
            if ylim != [None,None]: 
                plt.ylim(*ylim)
            plt.savefig(os.path.join(coutput["BLD Directory"],"_".join([str(coutput["Timestamp"]),coutput["BLD"],"Plot1.png"])))   # just in case

            # the suspicious fit plot
            if (fitgaussgo == 1) and (np.isinf(pcov[2][2]) is False) and (np.isinf(pcov[3][3]) is False): 
                try: 
                    textstr = '\n'.join((
                        r'$\mu=%.2f\pm%.2f$' % (x0, np.sqrt(pcov[2][2]),),
                        r'$\sigma=%.2f\pm%.2f$' % (sigma, np.sqrt(pcov[3][3]),),
                        r'$\mathrm{FWHM}=%.2f\mathrm{ps}$' % (ps, )))
                    plt.plot(t_df[x], gauss(t_df[x], *gauss_fit(t_df[x],t_df[y], errors)[0]), '-',color='r', label='fit')
                    ax.text(0.75, 0.95, textstr, color='k', fontsize='medium', verticalalignment='top', bbox=props,transform=ax.transAxes)
                except: 
                    print("There was an issue plotting the fit.") # should still let the raw data be plotted
            
            plt.legend(loc="upper left")
            plt.savefig(os.path.join(coutput["BLD Directory"],"_".join([str(coutput["Timestamp"]),coutput["BLD"],"Plot1.png"])))    
            plt.close() 

    # return list of data corresponding to the input parameters and dataset
    def generatefitline(self,inputnp,params,fit): 
        if fit == "gauss": 
            return [self.gauss(x,params['amp'],params['peak'],params['sigma'],params['float']) for x in inputnp]