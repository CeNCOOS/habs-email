import datetime
import time
import numpy as np
import pdb
def HABdate_to_ordinal(mydates,station):
    # dates are strings and may even have errors.
    # dates may have year first or last so need to figure out what type of
    # date structure it is...
    ld=len(mydates)
    orddates=[]
    cmon=['January','February','March','April','May','June','July','August','September','October','November','December']
    lc=len(cmon)
    for i in np.arange(0,ld):
        # is the first part a year or day or month?
        dtmp=mydates[i]
        dtmp=dtmp.replace("/"," ")
        dtmp=dtmp.replace("-"," ")
        dtmp=dtmp.replace(",","")
        dpiece=dtmp.split()
        yflag=0
        mflag=0
        if len(dpiece) < 3:
            # we have a problem (we know that there is one case)
            mmonth=int(dpiece[0])/100
            mday=int(dpiece[0])-mmonth*100
            myear=int(dpiece[1])
        else:
            # none start with a month?
            if int(dpiece[0]) > 32:
                # we have a year
                myear=int(dpiece[0])
                yflag=0
            else:
                # we have a month or a day...
                # but year will now be the last "piece"
                myear=int(dpiece[-1])
                yflag=-1
                if myear < 1000:
                    myear=myear+2000
            #so we know that either the start or end is the year
            #
            
            try:
                aval=int(dpiece[1])
                # if this works aval is either a month or a day
                if yflag==0:
                    mmonth=aval
                    #mflag=1
                    mday=int(dpiece[2])
                if yflag==-1:
                    mmonth=int(dpiece[0])
                    #mflag=0
                    mday=int(dpiece[1])
            except:
                for i in np.arange(0,lc):
                    if dpiece[1].lower() in cmon[i].lower():
                        mmonth=i+1
                mday=int(dpiece[0])          
            # okay we have the last one as a day
            #day=int(piece[2])
        try:
            if station=='Stearns':
                if mmonth==2:
                    if mday==5:
                        if myear==2017:
                            myear=2018
            theord=datetime.date(year=myear,month=mmonth,day=mday).toordinal()
        except:
            pdb.set_trace()
        orddates.append(theord)
    return orddates
        
                
