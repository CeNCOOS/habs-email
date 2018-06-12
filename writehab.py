import numpy as np
import datetime
import time
from netCDF4 import Dataset, date2index
import pickle
import pyworms as pwm
import uuid
import pdb
""" HAB e-mail NetCDF writing code.
This code writes the relative abundances from the e-mails an some ancillary data to a Station
named NetCDF file (i.e. HAB_Monterey.nc).
"""
# Let's write HAB info to a NetCDF file.
# Create a list of stations.
stations=['Santa Cruz','Monterey','Cal Poly','Newport','Stearns','Santa Monica','Scripps']
# create a list of ancillary variables
var1=['date','water temp','air temp','water color','dominant']
# define the NetCDF long name for these variables
long_name=['time',
           'Water Temperature',
           'Air Temperature',
           'Water Color',
           'Dominant Species']
# define the NetCDF standard names for the variables (CF compliant if possible).
standard_name=['time',
              'sea_water_temperature',
              'air_temperature',
              'sea_water_ocean_color',
              'dominant_species']
# some station specific meta-data for Darwin Core/OBIS to the best of my knowledge.
# These may not be correct!!!!
# Scripps
# Institution Code: SIO
# Institution LSID: urn:lsid:biocol.org:col:14844
# Cool URI: http://biocol.org/urn:lsid:biocol.org:col"14844
# UCSC
# Institution Code: UCSC<IH>
# urn:lsid:biocol.org:col:13097
# http://biocol.org/urn:lsid:biocol.rog:col:13097
# UCSB
# Institution Code: UCSB
# Cool URI http://grbio.org/cool/c9a4-gwd8
# CalPoly
# Institution code: CPSU
# http://grbio.org/cool/encc-nt08

# Institution Code: OBI<IH>
# urn:lsid:biocol.org:col:15734
# http://biocol.org/urn:lsid:biocol.org:col:15734
# UCLA
# Institution Code: LA<IH>
# urn:lsid:biocol.org:col:15420
# http://biocol.org/urn:lsid:biocol.org:col:15420
# USC
# Institution Code USC<IH>
# urn:lsid:biocol.org:15367
# http://biocol.org/urn:lsid:biocol.org:col:15367
# SJSU
# Institution Code SJSU
# urn:lsib:biocol.org:14977
# http://biocol.org/urn:lsid:biocol.org:col:14977
#
# list of institution codes
institutioncode=['UCSC',
                 'SJSU',
                 'CPSU',
                 'USC',
                 'UCSB',
                 'LA',
                 'SIO']
# location id's for stations
locationID=['http://marineregions.org/mrgid/19167',
            'http://marineregions.org/mrgid/19167',
            'http://marineregions.org/mrgid/32715',
            'http://marineregions.org/mrgid/32728',
            'http://marineregions.org/mrgid/19200',
            'http://marineregions.org/mrgid/32749',
            'http://marineregions.org/mrgid/19149']
# supposed lsid
lsid=['urn:lsid:biocol.org:col:13097',
      'urn:lsid:biocol.org:col:14977',
      '',
      'urn:lsid:biocol.org:col:15367',
      '',
      'urn:lsid:biocol.org:col:15420',
      'urn:lsid:biocol.org:col:14844']
# institutions
institution=['University of California, Santa Cruz',
             'Moss Landing Marine Lab, San Jose State University',
             'California Polytechnic Institute',
             'University of Southern California',
             'University of California, Santa Barbara',
             'University of California, Los Angeles',
             'Scripps Institude of Oceanography, University of California, San Diego']
# station latitudes
mylatitude=[36.9573,
          36.60513,
          35.107,
          33.6075,
          34.4100,
          34.0101,
          32.8681]
# station longitudes
mylongitude=[-122.0173,
           -121.88935,
           -120.741,
           -117.9288,
           -119.6856,
           -118.4961,
           -117.2503]
# load the plankton names
# This should probably be moved out of the loop.
fname="c:/test/plankton_names.txt"
content=[]
with open(fname) as f:
    for line in f:
        tmp=line.split()
        #pdb.set_trace()
        il=len(tmp)
        if il > 0:
            if tmp[0]=='#':
                # do nothing
                bad=1
            else:
                bad=0
                content.append(line)
content=[y.rstrip('\n') for y in content]
# creates a dictionary of the plankton names
lp=len(content)
# remove stuff not need for finding names
for ip in np.arange(0,lp):
    content[ip]=content[ip].replace(" spp.","")
    content[ip]=content[ip].replace(" group:","")
    content[ip]=content[ip].replace(" size class:","")
    content[ip]=content[ip].replace("(","")
    content[ip]=content[ip].replace(")","")
    content[ip]=content[ip].replace(" sanguinae","")
    content[ip]=content[ip].replace("-"," ")
# load the plankton name and WORMS ID.    
fnameid="c:/anaconda/plankton_id.txt"
species=[]
speciesid=[]
with open(fnameid) as g:
    for line in g:
        tmp=line.split()
        il=len(tmp)
        if il > 0:
            if tmp[0]=='#':
                pass
            else:
                try:
                    indy=tmp.index('#')
                except:
                    indy=0
                if indy > 0:
                    speciesid.append(tmp[indy-1])
                    ic=tmp[0:indy-1]
                    if len(ic) > 1:
                        thename=ic[0]+' '+ic[1]
                    else:
                        thename=ic[0]
                    species.append(thename)
                else:
                    speciesid.append(tmp[-1])
                    ic=tmp[0:-1]
                    if len(ic) > 1:
                        thename=ic[0]+' '+ic[1]
                    else:
                        thename=ic[0]
                    species.append(thename)
# ancillary data columns to output
columns=['date','water temp','air temp','water color','dominant']
ls=len(stations)
cs=np.arange(0,ls)
# load the pickle file created by the read_HAB_e-mail code.
HAB_station=pickle.load(open("mydatatest.pickle"))
# Now create and write the NetCDF files
# This will try to get close to the Darwin Core/OBIS standard.
for i in cs:
    oname=stations[i]
    oname=oname.replace(' ','_')
    fileout='HAB_'+oname+'.nc'
    newnc=Dataset(fileout,'w',format='NETCDF4')
    newnc.Conventions='CF-1.6'
    newnc.title='CeNCOOS/SCCOOS HAB monitoring station '+stations[i]
    newnc.institution=institution[i]
    newnc.institutionURL=''
    newnc.abstract='Weekly sampling of pier station for Harmful Algal Bloom, relative abundance'
    newnc.citation=institution[i]+' relative abundances of Harmful Algal species at '+station[i]+' wharf'
    newnc.source='Plankton nettows from fixed piers'
    newnc.summary=''
    newnc.creation_date=datetime.datetime.utcnow().isoformat()
#   need time_coverage_start and time_coverage_end but from other place
    newnc.license='These data may be used and redistributed for free but they are not \
                    intended for legal use, since they may contain inaccuracies.\
                    For use in publications please reference the Central and Northern \
                    California Ocean Observing System (CeNCOOS) and NOAA.  Neither the data \
                    provider, CeNCOOS, NOAA, nor the United States Government, nor any of \
                    their emplyees or contractors, makes any warranty, express or implied, \
                    including warranties of merchantability and fitness for a particular \
                    purpose, or assumes any legal liability for the accuracy, completeness, \
                    or usefulness, of this information.'
    newnc.infoURL='http://www.cencoos.org'
    newnc.featureType='timeSeries'
    newnc.naming_authority='www.cencoos.org'
    newnc.keywords_vocabular='GCMD Earth Science Keywords. Version 5.3.3'
#    newnc.keywords
    newnc.contact='cencoos_communications@mbari.org'
    newnc.creator_name='Fred Bahr'
    newnc.creator_email='flbahr@mbari.org'
    newnc.Metadata_Conventions='COARDS, CF-1.6, Unidata Dataset Discovery v1.0'
    newnc.standard_name_vocabulary='CF-1.6'
    newnc.history='CeNCOOS Asset'
    newnc.comment=''
    newnc.date_created=datetime.datetime.utcnow().isoformat()
    newnc.date_modified=''
    newnc.project='CeNCOOS'
    newnc.acknowledgement=''
    newnc.contributor=''
    newnc.contributor_role=''
    newnc.locationID=locationID[i]
    newnc.methods='Plankton net-tow'
    newnc.language='en'
    newnc.publisher='CeNCOOS'
    # stuff to add
    #newnc.eventID=
    #newnc.parentEventID=
    #newnc.occurrenceID (basically what our variable is)
    # set up spatial extent
    newnc.geodeticDatum='EPSG:4326'
    newnc.geospatial_lat_max=mylatitude[i]
    newnc.geospatial_lat_min=mylatitude[i]
    newnc.geospatial_lat_units='degrees_north'
    newnc.geospatial_lon_max=mylongitude[i]
    newnc.geospatial_lon_min=mylongitude[i]
    newnc.geospatial_lon_units='degrees_east'
    newnc.geospatial_vertical_max=0
    newnc.geospatial_vertical_min=-10
    newnc.geospatial_vertical_positive='down'
    newnc.geospatial_units='meters'
    newnc.geospatial_reference='mean_sea_level'
    newnc.createDimension('time',None)
    newnc.createDimension('station',1)
    
    time=newnc.createVariable('time','f8',('time',))
    time.units='days since 01-01-01 00:00:00'
    time.calendar='gregorian'
    time.long_name='time'
    time.standard_name='time'
    time.axis='T'
    time.ioos_category='time'
    time[:]=HAB_station[stations[i]]['date'].as_matrix()

    eventDate=newnc.createVariable('eventDate','f8',('time',))
    eventDate.units='days since 01-01-01 00:00:00'
    eventDate.calendar='gregorian'
    eventDate.long_name='eventDate'
    eventDate.standard_name='eventDate'
    eventDate[:]=HAB_station[stations[i]]['date'].as_matrix()
    # need to change this to decimalLongitude
    longitude=newnc.createVariable('longitude','f8',('station',))
    longitude.units='degrees_east'
    longitude.long_name='longitude'
    longitude.standard_name='longitude'
    longitude.axis='X'
    longitude.valid_min=-180
    longitude.valid_max=180
    longitude.ioos_category='Location'
    longitude.reference='WGS84'
    longitude.coordinate_reference_frame='urn:crs:EPSG::4326'
    # need to change this to decimalLatitude
    latitude=newnc.createVariable('latitude','f8',('station',))
    latitude.units='degrees_north'
    latitude.long_name='latitude'
    latitude.standard_name='latitude'
    latitude.axis='Y'
    latitude.valid_min=-90
    latitude.valid_max=90
    latitude.ioos_category='Location'
    latitude.reference='WGS84'
    latitude.coordinate_reference_frame='urn:crs:EPSG::4326'

    station_name=newnc.createVariable('station_name','str',('station',))
    station_name.cf_role='timeseries_id'
    station_name.long_name='Station Name'
    station_name.standard_name='station_name'
    newnc.variables['latitude'][:]=mylatitude[i]
    newnc.variables['longitude'][:]=mylongitude[i]
    newnc.variables['station_name']=stations[i]

    tmp=HAB_station[stations[i]]
    thekeys=[]
    for j in tmp.keys(): thekeys.append(j)
    lk=len(thekeys)
    varnames=thekeys[:]
    for j in np.arange(0,lk):
        varnames[j]=varnames[j].replace(' ','_')
        varnames[j]=varnames[j].replace('/','_')
    for k in np.arange(0,lk):
        if thekeys[k] != 'date':
            try:
                data=tmp[thekeys[k]]
                ld=len(data)
                try:
                    maxc=max(data.str.len())
                except:
                    pass
                abund=[]
                # convert abundance to numbers to plot in an order that is appropriate.
                # numbers are derived from the abundance limits.
                for m in np.arange(0,ld):
                    if ((data[m]=='None')or(data[m]=='none')):
                        abund.append(0)
                    elif ((data[m]=='x')or(data[m]=='X')):
                        abund.append(0)
                    elif data[m]=='NaN':
                        abund.append(np.nan)
                    elif ((data[m]=='r')or(data[m]=='R')or(data[m]=='rare')):
                        abund.append(1)
                    elif ((data[m]=='p')or(data[m]=='P')or(data[m]=='present')):
                        abund.append(9)
                    elif ((data[m]=='c')or(data[m]=='C')or(data[m]=='common')):
                        abund.append(24)
                    elif ((data[m]=='a')or(data[m]=='A')or(data[m]=='abundant')):
                        abund.append(50)
                    elif ((data[m]=='d')or(data[m]=='D')or(data[m]=='dominant')):
                        abund.append(75)
                    else:
                        abund.append(data[m])
                if ((varnames[k]=='dominant')or(varnames[k]=='water_color')):
                    myts='s'+str(maxc)
                    myvar=newnc.createVariable(varnames[k],'S1',('time',))
                    myvar.long_name=thekeys[k]
                    myvar.standard_name=thekeys[k]
                    
                    myvar.coordinate='time'
                    if varnames[k]=='water_color':
                        myvar.units='color scale'
                    else:
                        myvar.units='presence'
                    myvar[:]=data[:].as_matrix()
                else:
                    myvar=newnc.createVariable(varnames[k],'f8',('time',))
                    if varnames[k]=='air_temp':
                        myvar.units='deg C'
                    elif varnames[k]=='water_temp':
                        myvar.units='deg C'
                    else:
                        isp=content.index(thekeys[k])
                        myvar.scientificNameID=speciesid[isp]
                        myvar.taxonID=speciesid[isp]
                        if speciesid[isp] > 0:
                            atmp=pwm.aphiaRecordByAphiaID(speciesid[isp])
                            myvar.lsid=atmp['lsid']
                            
                        myvar.scientificName=species[isp]
                        myvar.units='presence'
                        myvar.decimalLongitude=mylongitude[0]
                        myvar.decimalLatitude=mylatitude[0]
                        myvar.occurrenceID='urn:catalog:'+institutioncode[i]+':plankton:'+speciesid[isp]
                        myvar.basisOfRecord='HumanObservation'
                        myvar.vernacularname=thekeys[k]
                        myvar.nameAccordintToID='itis'
                    myvar.long_name=thekeys[k]
                    myvar.standard_name=thekeys[k]
                    myvar.coordinate='time'
                    try:
                        myvar[:]=abund[:]
                    except:
                        pdb.set_trace()
            except:
                # no data for this variable
                pass
    newnc.close()

    # below are some of the OBIS stuff that need to be added?    
    
    # newnc.scientificName
    # newnc.scientificNameID
    # newnc.eventDate # this should correspond to the sample time?
    # newnc.decimalLatitude
    # newnc.decimalLongitude
    # newnc.occurrenceStatus # occurrence or absence of Taxon at site (sort of what we get)
    # newnc.basisOfRecord # nature of the data (i.e. LivingSpecimen, HumanObservation)
    # newnc.occurrenceID # examples-> urn:catalog:FMNH:Mammal:145732 urn:Isid:nhm.ku.edu:Herps:32
    # WoRMS (World Register of Marine Species) names must match to this
    # Darwin Core
    # newnc.vernacularname (aka common name)
    # newnc.recordedBy
    # newnc.kingdom
    # newnc.taxonRank
    # newnc.taxonRemarks
    # newnc.scientificNameAuthorship
    # newnc.indentifiedBy
    # newnc.dateIdentifide
    # newnc.identification.References
    # newnc.identification.Remarks
    # newnc.identification.Qualifier
    # newnc.typeStatus
    # newnc.occurrenceID
    # newnc.occurrenceStatus
    # newnc.recordedBy
    # newnc.individualCount
    # newnc.organismCount
    #organismQuantity (OBIS recommends to add measurements to eMoF)
    #organismQuantityType (OBIS recommends to add measurements to eMoF)
    #sex (OBIS recommends to add measurements to eMoF)
    #lifeStage (OBIS recommends to add measurements to eMoF)
    #behavior
    #associatedTaxa
    #occurrenceRemarks
    #associatedMedia
    #associatedReferences
    #associatedSequences
    #catalogNumber
    #preparations
    #basisOfRecord
    #institutionCode
    #collectionCode
    #collectionID
    #bibliographicCitation
    #modified
    #dataGeneralizations
    #decimalLatitude
    #decimalLongitude
    #coordinateUncertaintyInMeters
    #geodeticDatum
    #footprintWKT
    #minimumDepthInMeters
    #maximumDepthInMeters
    #locality
    #waterBody
    #islandGroup
    #island
    #country
    #locationAccordingTo
    #locationRemarks
    #locationID 
    #parentEventID
    #eventID
    #eventDate
    #type
    #habitat
    #samplingProtocol (OBIS recommends to add sampling facts to eMoF)
    #sampleSizeValue (OBIS recommends to add sampling facts to eMoF)
    #SampleSizeUnit (OBIS recommends to add sampling facts to eMoF)
    #samplingEffort (OBIS recommends to add sampling facts to eMoF)
    #materialSampleID
