import xml.etree.ElementTree as et
import os
import obspy as obs
from warnings import warn
from glob import glob
from obspy import read_inventory
try:
    from obspy.core.util import gps2DistAzimuth
except ImportError:
    from obspy.geodetics import gps2dist_azimuth
try:
    from obspy import fdsn
except ImportError:
    from obspy.clients import fdsn


from ANTS import antconfig as cfg

#==============================================================================================

def read_xml(filename):
    
    def recursive_dict(element):
        return element.tag, \
            dict(map(recursive_dict, element)) or element.text
    
    
    doc = et.parse(filename)
    
    return recursive_dict(doc.getroot())

#==============================================================================================

def find_coord(path_to_xml):
    sta = path_to_xml.split('/')[-1].split('.')[1]
    
    if not os.path.exists(path_to_xml):
        try:
            msg = 'stationxml file not found, trying to download from FDSN...'
            warn(msg)
            get_staxml(path_to_xml.split('/')[-1].split('.')[0],sta)
            
            inv = read_inventory(path_to_xml)
        
            sta = inv[0][0]
            staname = sta.code
            lat=sta.latitude
            lon=sta.longitude
            return str(staname), float(lat),float(lon)
        except:
            msg='Could not download stationxml file: Could not retrieve coordinates.'
            warn(msg)       
            return '000',0,0  
        
        #inf = read_xml(path_to_xml)
        
    else:
        try:
            inv = read_inventory(path_to_xml)
            print inv
        except KeyError: 
            msg='Faulty stationxml file: Could not retrieve coordinates.'
            warn(msg)       
            return '000',0,0

    
#==============================================================================================
    
def get_staxml(net,sta):
    client=fdsn.Client()
    outfile=cfg.datadir+'/stationxml/'+net+'.'+sta+'.xml'
    print outfile
    # Metadata request with obspy
    if os.path.exists(outfile)==False:
        client.get_stations(network=net,station=sta,filename=outfile,level='station')

#==============================================================================================

def get_coord_staxml(net1, sta1):

    try:
        (staname1,lat1,lon1)=find_coord(cfg.datadir+'/stationxml/'+net1+'.'+sta1+'.xml')
    
    except:
        return(0,0)
            
    
    return (lat1,lon1)

#==============================================================================
def get_geoinf(x1,y1,x2,y2,inp='coord'):
    
    if inp == 'coord':
        try:
            dist=gps2DistAzimuth(x1, y1, x2, y2)[0]
            az=gps2DistAzimuth(x1, y1, x2, y2)[1]
            baz=gps2DistAzimuth(x1, y1, x2, y2)[2]
        except NameError:
            dist=gps2dist_azimuth(x1, y1, x2, y2)[0]
            az=gps2dist_azimuth(x1, y1, x2, y2)[1]
            baz=gps2dist_azimuth(x1, y1, x2, y2)[2]
   
    return (x1, y1, x2, y2, dist, az, baz)

#==============================================================================================
    
def get_sta_info(stationlist,verbose=False):
    
    fid = open(stationlist,'r')
    idlist = fid.read().split('\n')
    
    for id in idlist:
        if verbose: print id
        if id == '': continue
        
        network = id.split('.')[0]
        sta = id.split('.')[1]
        try:
            get_staxml(network,sta)
        except:
            if verbose: print '\n ================== \
                               No xml downloaded for station \
                               ====================\n'+id
            continue

def get_antip_pt(lon,lat):
    """
    Return the coordinates (lon, lat) of the antipode.
    """
    
    if lon <= 0.:
        lon_new = lon + 180.
    else:
        lon_new = lon - 180.
        
    lat_new = -1.*lat
    
    return lon_new,lat_new
    