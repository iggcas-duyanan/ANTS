#plotting script
from obspy.iris import Client
from obspy.core import Trace,  read
from obspy.core.util.geodetics import gps2DistAzimuth
import os
import re
from TOOLS.read_xml import read_xml
import matplotlib.pyplot as plt
import numpy as np

def plot_dist(indir, xmldir, station, corrtype, stacktype, verbose=False, savefig=False):
    """
    A script to plot cross-correlation traces sorted by interstation distance.
    indir: string: path to directory containing results of stack.py
    xmldir: A directory containing the station xml files for all stations (to get the distances). These files must be in xml format and must be called network.station.sta_info.xml
    station: The 'reference': All other stations are plotted with respect to the station selected here and distance is distance to this station
    corrtype: string: cc or pcc
    stacktype: string: ls or pws; show the linear or the phase weighted stack (I need to implement first that actually the type is specified on the output file.
    """
    
    #Find the files containing a correlation of the 'reference' station
    sta=re.compile(station)
    lin=re.compile('lin_stack')
    
    ls=os.listdir(indir)
    stalist=[]
    
    for filename in ls:
        if sta.search(filename) is not None:
            if lin.search(filename) is not None:
                stalist.append(filename)
        else:
            continue
            
    
    #For all these files find the interstation distance, and plot accordingly
    for file in stalist:
        if verbose: print file
        inf=file.split('-')[0].split('.')+file.split('-')[1].split('.')
        stafile1=xmldir+'/'+inf[0]+'.'+inf[1]+'.sta_info.xml'
        stafile2=xmldir+'/'+inf[4]+'.'+inf[5]+'.sta_info.xml'
        
        
        correlation=read(indir+'/'+file)[0]
        
        if stacktype=='pws':
            psfile=lin.sub('phase_stack', file)
            pstack=read(indir+'/'+psfile)[0]
            correlation.data=correlation.data*pstack.data
            
        taxis=np.linspace(-(len(correlation.data)-1)/2/correlation.stats.sampling_rate,(len(correlation.data)-1)/2/correlation.stats.sampling_rate, len(correlation.data))
        
        if stafile1==stafile2:
           dist=0
        else:
           inf1=read_xml(stafile1)[1]
           inf2=read_xml(stafile2)[1]
           lat1=float(inf1['{http://www.data.scec.org/xml/station/}Network']['{http://www.data.scec.org/xml/station/}Station']['{http://www.data.scec.org/xml/station/}StationEpoch']['{http://www.data.scec.org/xml/station/}Lat'])
           lon1=float(inf1['{http://www.data.scec.org/xml/station/}Network']['{http://www.data.scec.org/xml/station/}Station']['{http://www.data.scec.org/xml/station/}StationEpoch']['{http://www.data.scec.org/xml/station/}Lon'])
           lat2=float(inf2['{http://www.data.scec.org/xml/station/}Network']['{http://www.data.scec.org/xml/station/}Station']['{http://www.data.scec.org/xml/station/}StationEpoch']['{http://www.data.scec.org/xml/station/}Lat'])
           lon2=float( inf2['{http://www.data.scec.org/xml/station/}Network']['{http://www.data.scec.org/xml/station/}Station']['{http://www.data.scec.org/xml/station/}StationEpoch']['{http://www.data.scec.org/xml/station/}Lon'])
           dist=gps2DistAzimuth(lat1, lon1, lat2, lon2)[0]
           
        plt.plot(taxis, correlation.data/np.max(correlation.data)+dist/10000)
        
    plt.xlabel('Lag Time (sec)')
    plt.ylabel('Cross-Correlation / Interstation distance')
    frame1=plt.gca()
    frame1.axes.get_yaxis().set_ticks([])
    
    if savefig==True:
        figname=indir+'/'+station+'_'+stacktype+'.'+corrtype+'.png'
        plt.savefig(figname, format='png')
        
    plt.show()
                     
            
            
            

            
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
def get_sta_info(indir, filt):
    client=Client()
    if os.path.exists(indir+'station_info')==False: os.mkdir(indir+'station_info')
    
    os.system('ls '+indir+' | grep '+ filt+' > temp.txt')
    fileid=open('temp.txt')
    filelist=fileid.read().split('\n')
    
    for file in filelist:
        try:
            inf=file.split('-')[0].split('.')+file.split('-')[1].split('.')
            outfile=indir+'/station_info/'+inf[4]+'.'+inf[5]+'.sta_info.xml'
            #Metadata request with obspy
            if os.path.exists(outfile)==False:
                client.station(inf[4], inf[5], filename=outfile)
        except IndexError:
            continue
    os.system('rm temp.txt') 
          