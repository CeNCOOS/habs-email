#
import numpy as np
def find_wtemp(wdindex,wtemp,m):
   if len(wdindex) > 0:
    for mi in np.arange(0,len(wdindex)):
        if wtemp[mi]=='(=C2=B0C):':
            wtemp[mi]=m[wdindex[mi]+3]
        if wtemp[mi]=='(=B0C):':
            wtemp[mi]=m[wdindex[mi]+3]
        if wtemp[mi]=='(\xc2\xb0C):':
            wtemp[mi]=m[wdindex[mi]+3]
        if wtemp[mi]=='(\xc2\xb0):':
            wtemp[mi]=m[wdindex[mi]+3]
        if wtemp[mi]=='(\xb0C):':
            wtemp[mi]=m[wdindex[mi]+3]
    wtemp=[e for e in wtemp if e not in ('prevailed','was','remains','dropped','declined','increased','</td>','this','emperature','rose','continued','remained','drops','and','associated')]
    for mw in np.arange(0,len(wtemp)):
        wtemp[mw]=wtemp[mw].replace("=C2=B0","")
        wtemp[mw]=wtemp[mw].replace("(=B0C):","")
        wtemp[mw]=wtemp[mw].replace("C","")
        wtemp[mw]=wtemp[mw].replace("\xc2\xb0","")
        wtemp[mw]=wtemp[mw].replace("\xb0","")
        wtemp[mw]=wtemp[mw].replace("NA","nan")
    return wtemp
def find_atemp(adindex,atemp,m):
    if len(adindex) > 0:
        for mi in np.arange(0,len(adindex)):
            if atemp[mi]=='(\xc2\xb0C):':
                atemp[mi]=m[adindex[mi]+3]
            if atemp[mi]=='(\xc2\xb0):':
                atemp[mi]=m[adindex[mi]+3]
            if atemp[mi]=='(\xb0C):':
                atemp[mi]=m[adindex[mi]+3]            
    for ma in np.arange(0,len(atemp)):
        atemp[ma]=atemp[ma].replace("\xb0","")
        atemp[ma]=atemp[ma].replace("\xc2","")
        atemp[ma]=atemp[ma].replace("NA","nan")
    if len(atemp)==0:
        atemp.append(np.nan)
    return atemp
# this might be a bit more complex as the line is harder to define.
def find_wcolor(wcindex,wcond,m,wcid):
    # wcid 1
    if wcid==1:
        wci=len(wcindex)
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
    # different response to work with...
    # wcid 2
    if wcid==2:
        wcii=len(wcindex)
        if wcii > 0:
            for iw in np.arange(0,wcii):
                tmpcolor=m[wcindex[iw]+2:wcindex[iw]+20]
                ltc=len(tmpcolor)
                for wi in np.arange(0,ltc):
                    if '(#' in tmpcolor[wi]:                    
                        colortmp=tmpcolor[1:wi+1]
                        for i in np.arange(0,len(colortmp)):
                            wcond[iw]=wcond[iw]+' '+colortmp[i]
    # yet another response to work with
    # wcid 3
    if wcid==3:
        if wcindex > 0:
            wcix=len(wcindex)
            for iw in np.arange(0,wcix):
                tmpcolor=m[wcindex[iw]+2:wcindex[iw]+20]
                if 'Tide:' in tmpcolor:
                    nind=[i for i,q in enumerate(tmpcolor) if q=='Tide:']
                    if len(nind) > 0:
                        colortmp=tmpcolor[1:nind[0]]
                        #pdb.set_trace()
                        for i in np.arange(0,len(colortmp)):
                            wcond[iw]=wcond[iw]+' '+colortmp[i]
    return wcond
                    
    
    
