import numpy as np
import datetime
import time
import urllib2
import pdb
import json
import email
import pandas as pd
from HABdate_to_ordinal import HABdate_to_ordinal
from find_wtemp import find_wtemp
from find_wtemp import find_atemp
from name_len import name_len
import matplotlib.pyplot as plt
import pickle
#
""" This is code to read HAB e-mail messages from zimbra and create a pickle file of the data
"""
# set up month names for reading
months=['January','February','March','April','May','June','July','August','September','October','November','December']
mons=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
# set up e-mail credentials so we can access e-mails
# I will NOT post creds.json as that contains both my username and pw
# This section reads the username and password from a json file to allow access to the e-mail.
with open('creds.json') as f:
    data=json.load(f)
    username=data['username']
    password=data['password']
# instantiate the password manager
password_mgr=urllib2.HTTPPasswordMgrWithDefaultRealm()
top_level_url='YOUR URL GOES HERE'
# add your password to the password manager
password_mgr.add_password(None,top_level_url,username,password)
# create a handler to authentic username and password
handler=urllib2.HTTPBasicAuthHandler(password_mgr)
# actually login and open the e-mail directory.
opener=urllib2.build_opener(handler)
# Now look at my inbox subdirectory HAB_email and get message ID's
testurl='https:YOUR URL GOES HERE /HAB_email?fmt=json'
# open the mailbox
opener.open(testurl)
urllib2.install_opener(opener)
test=urllib2.urlopen(testurl)
# read the messages in the mailbox
y=test.read()
# decode the massages
kk=json.JSONDecoder().decode(y)
mykeys=kk.keys()
ck=kk[mykeys[0]]
letterids=[]
# create a list of the e-mail id's so we can access individual messages
for ii in np.arange(0,len(ck)):
    letterids.append(ck[ii]['id'])
ll=np.arange(0,len(letterids))
#
# okay load my "dictionary" of plankton names. This could be shoved off to a function.
# This should probably be moved out of the loop.
# This creates a dictionary of the plankton names from a simple text file.  Ths was done so
# it would be easy to edit the names as we come across new names.
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
# number of planton names in my "dictionary"
lp=len(content)
# We need to condense the list a bit for output of data
# So how do we do this?
# need to treat Rhizosolenia and Rhizosolenia spp the same
# the section below removes superfluous information to cut down the number of actual names.
# These are still unique names for what is observed.
poutput=[]
myp=content[:] # make an actual copy so we can manipulate and not change original
for ip in np.arange(0,lp):
   myp[ip]=myp[ip].replace(" spp.","")
   myp[ip]=myp[ip].replace(" group:","")
   myp[ip]=myp[ip].replace(" size class:","")
   myp[ip]=myp[ip].replace("(","")
   myp[ip]=myp[ip].replace(")","")
   myp[ip]=myp[ip].replace(" sanguinae","")
   myp[ip]=myp[ip].replace("-"," ")
myp=list(sorted(set(myp))) # try to get just the unique names for output
myp.remove('Acantharians') # just one case of plural so remove
# We may want to fine tune the list myp

# 
# Set up data arrays for data
# Question is just what do we want to do here?
#
# We have ? piers? 7
# We have lp number of plankton
# can't append in a ragged array fashion python complains
# so we have 7 arrays?
# each array is lp plankton by n-days?
#
# data frame
# set up an array of station names (we can increase if we get more stations to the north)
stations=['Santa Cruz','Monterey','Cal Poly','Newport','Stearns','Santa Monica','Scripps']
# set up some other columns to add to our output beyond the plankton names
columns=['date','water temp','air temp','water color','dominant']
# need a set for phyto names
# let us ignore this for the moment and see if we can load water temp and dates
blankdict={}
HAB_station={}
clen=len(columns)
slen=len(stations)
for ic in np.arange(0,clen):
    blankdict.update({columns[ic]:pd.Series(np.nan)})
plen=len(myp) #length of unique plankton names (sort of...)
for ipi in np.arange(0,plen):
    blankdict.update({myp[ipi]:pd.Series(np.nan)})
for si in np.arange(0,slen):
    HAB_station[stations[si]]=pd.DataFrame(blankdict)
# we now have a data frame for each sampling site
# lets see if we can actually load data into it...
counts=np.zeros(7)
# Start looping through the messages
# This where the work gets done.
for jj in ll:
    mid=letterids[jj]
    # actually grab a particular message
    url='https:YOUR URL GOES HERE ?id='+mid
    opener.open(url)
    urllib2.install_opener(opener)
    test=urllib2.urlopen(url)
    x=test.read()
    # for encoded e-mail we want to do the next few lines
    msg=email.message_from_string(x)
    whom=msg['From']
    # some code to check that we are actually working
    print '\n'
    print str(jj)+' '+whom+' '+mid
    # determine if the e-mail needs to be decoded
    myfmt=msg.get_content_type()
    # get the actual message body (aka the payload)
    mytest=msg.get_payload()
    # check if we try to decode or just use the result
    try:
        mybody=mytest[0].get_payload(decode=True)
    except:
        mybody=mytest[:]
    # Do we use x or have replaced this with mybody below?
    # convert some stuff we don't care about to either nothing or spaces
    # this will help in parsing the message payload.
    x=x.replace("\r","")
    x=x.replace("\t"," ")
    x=x.replace("=\n"," ")
    x=x.replace("=09"," ")
    x=x.replace("&nbsp;"," ")
    x=x.replace("<br>"," ")
    x=x.replace("\xa0"," ")
    x=x.replace("\xc2"," ")
    # remove some problematic characters 
    mybody=mybody.replace("\r","")
    mybody=mybody.replace("\t"," ")
    mybody=mybody.replace("=\n"," ")
    mybody=mybody.replace("=09"," ")
    mybody=mybody.replace("&nbsp;"," ")
    mybody=mybody.replace("\xa0"," ")
    mybody=mybody.replace("\xc2","")
    #mybody=mybody.replace("-","") # Doing this makes it fail
    # make an actual copy and not a link to the array
    # we do this since we want a body that is not split also 
    my=mybody[:]
    #my=x[:] # make a copy?
    my=my.replace(" ","")
    my=my.replace("\t","")
    my=my.replace("\n","")
    # split the message into words based upon spaces
    # still might have funky characters.
    m=mybody.split()
    #
    # Using the name to define the length of the location name to find
    # name is the number of words to look for +1
    name=name_len(whom)
    # search for the location in the e-mail
    mis=[i for i, y in enumerate(m) if (y=="LOCATION:")or(y=="Location:")]
    # we have a problem there is no space between DATE:16-Jan-2018 ! how do we find this issue?
    dis=[i for i, y in enumerate(m) if (y=="DATE:")or(y=="Date:")]
    # we have an issue if DATE: is not in the file
    if len(dis)==0:
        mys1=set(months)
        mys2=set(mons)
        mymm1=[jk for jk in m if jk in mys1]
        if len(mymm1)> 0:
            dis=[i for i, y in enumerate(m) if y==mymm1[0]]
        mymm2=[jk for jk in m if jk in mys2]
        if len(mymm2)> 0:
            dis=[i for i, y in enumerate(m) if y==mymm2[0]]
        nodate=0
    else:
        nodate=1
    lm=np.arange(0,len(mis))
    ld=np.arange(0,len(dis)) # we've stripped the header info now
    ln=np.arange(1,name)
    mylocation=[]
    # this is set up to fix some problems with finding locations
    # some of the messages don't have the location word so thse are to place those messages.
    if whom=='"Carter, Melissa" <mlcarter@ucsd.edu>':
        mylocation.append('Scripps Pier, La Jolla CA')
    if whom=='Melissa Carter <mlcarter@ucsd.edu>':
        mylocation.append('Scripps Pier, La Jolla CA')
    if whom=='Rebecca Shipe <rshipe@gmail.com>':
        mylocation.append('Santa Monica Pier')
    if whom=='Leandre Ravatt':
        mylocation.append('Cal Poly Center for Coastal Marine Science Pier, Avila Beach')
    for i in lm:
        myl=""
        for j in ln:
            myl=myl+m[mis[i]+j]+' '
        mylocation.append(myl)
    if len(mylocation) > 0:
        print mylocation
    else:
        print "no location info"
    #
    # At this point we should have location information
    # Need to set a flag for which site based upon list we set up?
    # What if multiple values of mylocation?  All values are from the same site?  So far this is true.
    #
    mylocation[0]=mylocation[0].replace("'","")
    siteindex=[i for i,y in enumerate(stations) if y in mylocation[0]]
    # site index now should have a value from 0 to 6
    if len(siteindex) <= 0:
        # we did not get a location so halt and work to fix this
        # This is since we use location for id of data.
        pdb.set_trace()
    # Now we actually get the date deal with the case where we don't have the word DATE first
    if nodate==0:
        mydate=m[dis[0]-1].replace('*','')+' '+m[dis[0]]+' '+m[dis[0]+1].replace('*','')
    mydates=[]
    dateind=[]
    htmlstart=0
    # NOw to deal with when we actually have the word Date or DATE
    if nodate==0:
        mydates.append(mydate)
        dateind.append(dis[0])
    else:
        for i in ld:
            isitit=m[dis[i]+1]
            if len(isitit) < 3:
                mydstr=m[dis[i]+1]+'-'+m[dis[i]+2]+'-'+m[dis[i]+3]
                mydates.append(mydstr)
            else:
                mydates.append(m[dis[i]+1])
            dateind.append(dis[i]+1)
        # Okay we need to figure out which dateind is the one to use
        # also need to know if dates are identical or not (i.e. more that one obs period can be in a message)
        # check for ">" in word before if so pop that id
        if len(dis) > 0:
            if ">" in m[dis[0]-1]:
                zx=dis[:]
                dis.pop(0)
                if len(dis)==0:
                    dis=zx
                #mydates.pop(0)
        if len(dis) > 0:
            if "<br>" in m[dis[-1]+1]:
                htmlstart=dis[-1] # html portion of mail message starts so ignore it as it repeats previous data
                #mydates.pop(len(dis)-1)
                xz=dis[:]
                dis.pop(len(dis)-1)
                if len(dis)==0:
                    dis=xz
        if len(mydates) > 0:
            if "<br>" in mydates[-1]:
                mydates.pop(-1)
        if htmlstart==0:
            htmlstart=len(m)
    if htmlstart==0:
        htmlstart=len(m)
    #
    # Okay we have the dates in the file (hopefully they are unique)
    #
    myords=HABdate_to_ordinal(mydates,stations[siteindex[0]])
    # Now to decode the dates and make them into something actually useful
    # This loop puts the data into the data frame at the spot we want it.
    for nd in np.arange(0,len(mydates)):
        HAB_station[stations[siteindex[0]]].at[counts[siteindex[0]],'date']=myords[nd]
#        HAB_station[stations[siteindex[0]]].at[counts[siteindex[0]],'date']=mydates[nd]
        counts[siteindex[0]]=counts[siteindex[0]]+1
    #
    # The variable dis (see above) tells us when we are in the second part of the message
    # for a multi-day sample message
    #
    dgind=[i for i, y in enumerate(m) if (y=="DOMINANT")or(y=="Dominant")]
    # okay there may or may not be a parenthesis (diatoms,dinoflagellates)
    lg=np.arange(0,len(dgind))
    mydom=[]
    # This next section looks for the dominant phytoplankton group.
    for i in lg:
        # look at second word to check that it is GROUP or Group or group
        wtmp=m[dgind[i]+1]
        if ("GROUP" in wtmp)|("Group" in wtmp)|("group" in wtmp):        
            # look at first word after group does it contain a "("
            wtmp=m[dgind[i]+2]
            wi=wtmp.find('(')
            if wi >= 0:
                wtmp=m[dgind[i]+3]
                wj=wtmp.find(')')
                if wj >=0:
                    mydom.append(m[dgind[i]+4])
                else:
                    mydom.append(m[dgind[i]+3])
            else:
                mydom.append(m[dgind[i]+2])
    # we need to know how many days worth of data are in the file
    ndays=len(dis)
    ndflag=0
    if ndays > 1:
        # set up an way to keep them seperate
        #pdb.set_trace()
        ndflag=nd-1
        
    # need to set up a way to keep the days seperate
    # we need the regular expression module
    import re
    # okay this is returning the wrong number of things....
    from find_plankton_word import find_plankton_word
    # list of possible abundance words after then name
    abundance=['x','r','p','c','a','none','rare','present','abundant','x:','r:','p:','c:','a:']
    # list of possible abundance words before the plankton name
    abundbefore=['x:','r:','p:','c:','a:','x','r','p','c','a']
    # list of words that can follow the keyed on plankton name
    awafter=['sanguinae','spp.','pseudogonyaulax','brown','cf','azicorum','candelabrum','divarcatum','furca','fusus',
             'lineatum','macroceros','penatogonum','tripos','teres','acuminata','caudata','fortii','mitra','brevis',
             'polyedra','polyedrum','cf','gracile','micans','delicatissima','seriata','sanguinea:']
    # look for each plankton word in "dictionary"
    for l in np.arange(0,lp):
        # test case to find Akashiwo and break 
        #if content[l]=='Akashiwo':
        #    pdb.set_trace()
        wordind=find_plankton_word(my,m,content[l])
        # is the word index in the first day in the file or the second day?
        # number of words in plankton word
        pword=content[l].split()
        lpw=len(pword)
        # which myp do we have?
        # this is too simple, it ignores pseudo nitzschia delicatissima from seriata...
#        lpp=np.arange(0,len(myp))
#        for i in lpp:
        ptmp=content[l]
        ptmp=ptmp.replace(" spp.","")
        ptmp=ptmp.replace(" group:","")
        ptmp=ptmp.replace(" size class:","")
        ptmp=ptmp.replace("(","")
        ptmp=ptmp.replace(")","")
        ptmp=ptmp.replace(" sanguinae","")
        ptmp=ptmp.replace("-"," ")
        if ptmp=='Acantharians':
            ptmp='Acantharian'
        plank=[i for i,y in enumerate(myp) if y==ptmp]
    # now we have the location of the plankton word check the word before and after it
    # so what words are we looking for?
    # x,X c,C P,p R,r None Rare Present Common Abundant a,A
    # Now we are checking for the abundance characters.... Look both before and after the plankton word.
        lw=np.arange(0,len(wordind))
        for ia in lw:
            stuffit=np.nan
            if wordind[ia] > dis[0]:
                # check if ndays > 1
                if ndays > 1:
                    if wordind[ia] < dis[1]:
                        # corresponds to first day in file so two back in the count
                        stuffit=counts[siteindex[0]]-2
                    else:
                        if (wordind[ia] > dis[1])&(wordind[ia] < htmlstart):
                            # corresponds to second day in file so since count is from 1 we need to subtract 1
                            stuffit=counts[siteindex[0]]-1
                else:
                    # only one day in file since count is +1 subtract 1 to get last entry
                    stuffit=counts[siteindex[0]]-1
            #if ndays > 1:
            #    pdb.set_trace()
            # some e-mails have both "plain text" and "html" if it has "html" we don't want to count things
            # twice to break out of the loop.
            if wordind[ia] > htmlstart:
                break
            wordbefore=m[wordind[ia]-1]
            wordafter=m[wordind[ia]+lpw]
            # need to distinguish between one word and multiword answers that start with the same word
            # now we don't get single word answers.....
            if (wordafter in awafter)&(lpw==1):
                break
            wordbefore=wordbefore.lower()
            wordafter=wordafter.lower()
            #if l==5:
            #    pdb.set_trace()
            # this is clean up so that we can reset and find the index.
            try:
                del abind
                del afind
            except:
                pass
            abind=[i for i,q in enumerate(abundbefore) if q==wordbefore]
            # commented out logic is to show thoughts that didn't pan out.
            #if len(abind)==0:
            #afind=[i for i,q in enumerate(abundance) if ((q==wordafter)&(q not in abundbefore)) ]
            afind=[i for i,q in enumerate(abundance) if (q==wordafter) ]
            #else:
            #    afind=[]
            
            myabund=[]
            if len(abind) >0:
                if (abundance[abind[0]] != 'x'):
                    myabund=abundbefore[abind[0]]
                else:
                    pass
                    #myabund='NaN'
            if len(afind) >0:
                #if (abundance[afind[0]] !='x') &(abundance[afind[0]]!='none'):
                if (abundance[afind[0]] !='x'):
                    myabund=abundance[afind[0]]
                else:
                    pass
                    #myabund='NaN'
            tmp=content[l]
            try:
                if myabund=='none':
                    myabund='NaN'
            except:
                pass
##            if l==3:
##                pdb.set_trace()
            if len(myabund) > 0:
                myabund=myabund.replace(":","")
                HAB_station[stations[siteindex[0]]].at[stuffit,myp[plank[0]]]=myabund
#            if jj==0:
#                if ptmp=='Skeletonema':
#                    pdb.set_trace()
                #if len(dis) > 1:
                #    if wordind[ia] > dis[1]:
                #        daystr='second '
                #    else:
                #        daystr='first '
                #else:
                #    daystr='first '
                ##print "The abundance of "+tmp+" is "+myabund+' for '+daystr+'day in file'

    #if jj==0:
    #    pdb.set_trace()
    from find_word_val import find_word_val
    [wdindex,wtemp]=find_word_val(my,m,'Water Temperature:')
    wtemp=find_wtemp(wdindex,wtemp,m)
    # need code to see if we want to stop this (note no ":" here)
    [wdindex,wtemp]=find_word_val(my,m,'Water Temperature')
    wtemp=find_wtemp(wdindex,wtemp,m)
    # some where we need to check if len(wdindex) > 0 to sort between these
    [wdindex,wtemp]=find_word_val(my,m,'Water Temp')
    wtemp=find_wtemp(wdindex,wtemp,m)
    [adindex,atemp]=find_word_val(my,m,'Air Temperature:')
    atemp=find_atemp(adindex,atemp,m)
    # again need to check if adindex > 0
    [adindex,atemp]=find_word_val(my,m,'Air Temp')
    atemp=find_atemp(adindex,atemp,m)
    # thise are just checks to make sure we are retrieving the correct thing.
    #print "My dates"
    #print dis
    #print mydates
    #print "Air Temperature"
    #print atemp
    # Now let's put the air temperature in our data frame
    # Will need to check that stuff doesn't get offset if we have more than one day in a file.
    na=len(atemp)
    no=len(myords)
    # do some "clean up"/checks on the air temperature to make sure it is a number
    if na > no:
        try:
            junk=round(float(atemp[0]),2)
        except:
            del atemp[0]
    for nd in np.arange(0,len(atemp)):
        if atemp[nd]=='(=B0C):':
            if m[adindex[nd]+3]=='NA':
                atemp[nd]=np.NaN
            else:
                atemp[nd]=m[adindex[nd]+3]        
        if "/" in str(atemp[nd]):
            atemp[nd]=atemp[nd].replace("/",".")
        if stations[siteindex[0]] in 'Santa Cruz':
            # convert from deg F to deg C for the only station that has value as deg F.
            atemp[nd]=round((float(atemp[nd])-32)*5.0/9.0,1)
        try:
            atemp[nd]=round(float(atemp[nd]),2)
        except:
            # stop.  We hit a case not covered....
            pdb.set_trace()
        # fill in our data frame
        HAB_station[stations[siteindex[0]]].at[counts[siteindex[0]]-ndays+nd,'air temp']=atemp[nd]
    #
    # Let's do the same for water temperature
    nw=len(wtemp)
    if nw > no:
        try:
            junk=round(float(wtemp[0]),2)
        except:
            del wtemp[0]
    for nd in np.arange(0,len(wtemp)):
        if "/" in str(wtemp[nd]):
            wtemp[nd]=np.nan
        try:
            wtemp[nd]=round(float(wtemp[nd]),2)
        except:
            # stop. we hit a case not covered....
            pdb.set_trace()
        # fill in our data frame
        HAB_station[stations[siteindex[0]]].at[counts[siteindex[0]]-ndays+nd,'water temp']=wtemp[nd]
    ndom=len(mydom)
    # put the dominant type into the data frame
    for ni in np.arange(0,ndom):
        if mydom[ni]=='even':
            mydom[ni]='even mix'
        if mydom[ni]=='Equal':
            mydom[ni]='even mix'
        HAB_station[stations[siteindex[0]]].at[counts[siteindex[0]]-ndays+ni,'dominant']=mydom[ni]
    # look for water color/visibility/conditions 
    [vindex1,vis1]=find_word_val(my,m,'Visibility:')
    [vindex2,vis2]=find_word_val(my,m,'Water Visibility:')
    [wcindex,wcond]=find_word_val(my,m,'Water Conditions:')
    wci=len(wcindex)
    wcolor=[]
    if wci > 0:
        for iw in np.arange(0,wci):
            tmpcolor=m[wcindex[iw]+2:wcindex[iw]+20]
            if 'NOAA' in tmpcolor:
                nind=[i for i,q in enumerate(tmpcolor) if q=='NOAA']
                if len(nind) > 0:
                    colortmp=tmpcolor[1:nind[0]+5]
                    for i in np.arange(0,len(colortmp)):
                        wcond[iw]=wcond[iw]+' '+colortmp[i]
            if 'Visibility:' in tmpcolor:
                nind=[i for i,q in enumerate(tmpcolor) if q=='Visibility:']
                if len(nind) > 0:
                    colortmp=tmpcolor[1:nind[0]]
                    for i in np.arange(0,len(colortmp)):
                        wcond[iw]=wcond[iw]+' '+colortmp[i]
                    
    # how do we know how much beyond we need to search?...
    #print wcond
    [wci1,wcolor1]=find_word_val(my,m,'Water Color/Code:')
    wcii=len(wci1)
    if wcii > 0:
        for iw in np.arange(0,wcii):
            tmpcolor=m[wci1[iw]+2:wci1[iw]+20]
            ltc=len(tmpcolor)
            for wi in np.arange(0,ltc):
                if '(#' in tmpcolor[wi]:                    
                    colortmp=tmpcolor[1:wi+1]
                    for i in np.arange(0,len(colortmp)):
                        wcolor1[iw]=wcolor1[iw]+' '+colortmp[i]
    [wci2,wcolor2]=find_word_val(my,m,'Water Color:')
    #print wcolor1
    if wci2 > 0:
        wcix=len(wci2)
        for iw in np.arange(0,wcix):
            tmpcolor=m[wci2[iw]+2:wci2[iw]+20]
            if 'Tide:' in tmpcolor:
                nind=[i for i,q in enumerate(tmpcolor) if q=='Tide:']
                if len(nind) > 0:
                    colortmp=tmpcolor[1:nind[0]]
                    #pdb.set_trace()
                    for i in np.arange(0,len(colortmp)):
                        wcolor2[iw]=wcolor2[iw]+' '+colortmp[i]
    #print wcolor2
    [wci3,wcolor3]=find_word_val(my,m,'COLOR:')
    if len(wci3) > 0:
        [wchl,chl]=find_word_val(my,m,'CHL')
        if len(wchl) > 0:
            for wiii in np.arange(2,(wchl[0]-wci3[0])):
                wcolor3[0]=wcolor3[0]+' '+m[wci3[0]+wiii]
    #print wcolor3
    [tindex1,times1]=find_word_val(my,m,'Time:')
    [dindex1,dates1]=find_word_val(my,m,'Date:')
    if len(wcindex) > 0:
        wcolor=wcond
        del wcond
        del wcindex

    if len(wcolor) == 0:
        if len(wci1) > 0:
            wcolor=wcolor1
            del wci1
            del wcolor1
    if len(wcolor)==0:
        if len(wci2) > 0:
            wcolor=wcolor2
            del wcolor2
            del wci2
    if len(wcolor)==0:
        if len(wci3) > 0:
            wcolor=wcolor3
            del wci3
            del wcolor3
    try:
        lc=len(wcolor)
        for ni in np.arange(0,lc):
            HAB_station[stations[siteindex[0]]].at[counts[siteindex[0]]-ndays+ni,'water color']=wcolor[ni]
    except:
        pass
# create a pickle file of the dataframe from the e-mails.
# code is too long so stop and this point and let another piece of code write out to NetCDF.
f=open('mydatatest.pickle','wb')
pickle.dump(HAB_station,f)
f.close()









