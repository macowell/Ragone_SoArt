# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 15:44:44 2016

@author: martincowell
Ragone Plot State of the Art
"""
import pandas as pd
from pandas import * 
import glob  
import math
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from pint import UnitRegistry
ureg = UnitRegistry()
import datetime

## USER INPUTS: 

# normalize Energy and Power by 
normalize = 'Volume'
unit = {'normalize': 'cm^3', 'Power': 'W', 'Energy': 'Wh'} 

##==================================================================
## read data from all csv files in directory
#   web plot digitizer tool here:
#   http://arohatgi.info/WebPlotDigitizer/

#   original importing code here:
#   http://www.randalolson.com/2012/06/26/using-pandas-dataframes/
##==================================================================

dataLists = {} 
print('Data files included: ')
for folder in glob.glob("data/*"):  
    print(folder)
      
    dataLists[folder.split("/")[1]] = []  
      
    for datafile in glob.glob(folder + "/*.csv"):
        print(datafile)
        dataLists[folder.split("/")[1]].append(read_csv(datafile))
print('import completed', '\n')

## convert units to desired

for author in dataLists.keys():
    for index in dataLists[author]:
        n = float(index[normalize][1]) * ureg.parse_expression(str(index[normalize][0]))
        if n.magnitude:                 # only normalize if normalization quantity is in the csv file
            print(str(author) + ' ' + str(index['Sample Description'][0]) +  ' normalized by: ' + str(unit['normalize']))
            Ptemplist = []
            Ptemplist.append(str(unit['Power'] + '/' + unit['normalize']))        
            for element in index['Power'][1:]:
                a = float(element) * ureg.parse_expression(str(index['Power'][0]))
                b = a / n
                c = b.to(ureg.parse_expression(Ptemplist[0]))
                Ptemplist.append(c)
            index['P_norm'] = Ptemplist
            
            Etemplist = []
            Etemplist.append(str(unit['Energy'] + '/' + unit['normalize']))
            for element in index['Energy'][1:]:
                a = float(element) * ureg.parse_expression(str(index['Energy'][0]))
                b = a / n
                c = b.to(ureg.parse_expression(Etemplist[0]))
                Etemplist.append(c)
            index['E_norm'] = Etemplist
        if not(n.magnitude):                # record zeros if no normalization data in the csv
            index['P_norm'] = 0
            index['P_norm'] = 0

## plot data
figsize = (9,6)
plt.figure(figsize=figsize)
ax3 = plt.gca()
ax3.set_yscale('log')
ax3.set_xscale('log')
plt.grid(b=True, which='major', color='gray', linestyle='-') 
#history = []
#matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
#csfont = {'fontname':'Comic Sans MS'}
#hfont = {'fontname':'Comic Sans MS'}

#colors = ['r','y','b','g','m','k']                 # initialize random colors
#markers = ['o','s','^','D','*','p']                # initialize random markers
count = 0
for author in dataLists.keys():
    for index in dataLists[author]:
        if index['P_norm'][0]:              # only plot data that could be normalized
            x = []
            y = []
    #        c = colors[count%len(colors)]                  #use random colors
    #        m = markers[count//len(colors)]                #use random markers
            c = str(index['Color'][0])                      #use preset colors
            m = str(index['Shape'][0])                      #use preset markers
            desc = index['Sample Description'][0]
            for element in index['P_norm'][1:]:
                x.append(element.magnitude)
            for element in index['E_norm'][1:]:
                y.append(element.magnitude)
            ax3.scatter(x,y,s=60,c=c, marker=m, label=desc, alpha = 0.75)
            #history.append(index['Volume'][1])
            count = count+1

if normalize == 'Volume':
    xlabstr = 'Power density'
    ylabstr = 'Energy density'
if normalize == 'Mass':
    xlabstr = 'Specific Power'
    ylabstr = 'Specific Energy'
if normalize != 'Volume' and normalize != 'Mass':
    xlabstr = 'Normalized Power'
    ylabstr = 'Normalized Energy'
    
ax3.set_title('Energy Storage: capacity and rate limits')
ax3.set_ylabel((ylabstr + '  [$' + unit['Energy'] + ' / ' + unit['normalize'] + '$]'), style='normal')
ax3.set_xlabel((xlabstr + '  [$' + unit['Power'] + ' / ' + unit['normalize'] + '$]'), style='normal')
ax3.set_ylim([0.0000001,1])
matplotlib.pylab.legend(loc = 2, fontsize = 'small', bbox_to_anchor=(1.05,1), borderaxespad=0.)

## create isotemp lines
#This doesn't work yet. Having trouble reading the proper units of time between the axes
xmin, xmax = plt.xlim()
ymin, ymax = plt.ylim()
xdomain = np.log10(xmax/xmin)
yrange = np.log10(ymax/ymin)
Time = ureg.parse_expression(unit['Energy'])/ureg.parse_expression(unit['Power'])
print(Time)
unit['Time'] = Time.to_base_units

## Save plot
datestr = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
plt.savefig(str('plots/output_plots/' + str(datestr) + '_Ragone.pdf'), bbox_inches="tight", transparent = 'True' ) 

##Display plot
matplotlib.pylab.show()
