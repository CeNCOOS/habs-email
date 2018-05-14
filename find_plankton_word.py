#
# A module to parse e-mail text for a plankton word
# input is the e-mail text sans spaces,tabs and newlines
# input is the number of words in the e-mail
# input is the actual word to find this is currently a strict match (case counts)
# The function returns the word index of the plankton word or an empty list
# The code will NOT catch misspellings.
import re
import numpy as np
import pdb
def find_plankton_word(mytext,myword,plankton):
    """ find_plankton_word(mytext,myword,plankton) module to find a particular plankton word
    in the e-mail payload as both the word and the whole text.
    mytext is the whole payload of the e-mail without breaking it up so we can count characters.
    myword is the words in the payload that we want to match against.  The output is the index
    where the word occurrs.
    """
# def find_plankton_word(emailtext,plankton):
# mytext=emailtext.replace(" ","")
# myword=emailtext.split()
    #mytext=mytext.replace("-","")
# to make case insensitive
# plankton=plankton.lower()
    # Code could be made to do the remove spaces and parse words....
    # mytext is the e-mail message with spaces and some special characters removed
    # myword is the e-mail split into words based on space/tab/newline
    # plankton is the plankton word to search for (i.e. 'Akashiwo')
    # this code so far only works for single word searches....
    pword=plankton.split()
    lp=len(pword)
    wordstart=[]
    wordstop=[]
    wordind=[]
    iflag=0
    nospacep=plankton.replace(" ","")
    # need to find multiple word plankton word
    for k in re.finditer(nospacep,mytext):
#    for k in re.finditer(plankton,mytext):
        wordstart.append(k.start())
        wordstop.append(k.end())
        iflag=1
    if iflag==0:
        # no match
        return wordind
    lko=np.arange(0,len(myword)) # total number of "words" in the e-mail
    lw=np.arange(0,len(wordstart)) # number of instances of the plankton word we need to find
    for myi in lw:
        msum=0
        for j in lko:
            msum=msum+len(myword[j]) # sum up the lenght of words to find which index
            #print str(msum)+' '+str(j)
            #print myword[j]
            # j corresponds to the text index location
            if int(msum) >= wordstart[myi]:
                if msum==wordstart[myi]:
                    wordind.append(j+1)
                else:
                    wordind.append(j)                    
                break # this should only work on the inner for loop and not the outer
    # okay we should have the index of all words that match the plankton word sent in
    # for some reason we are off by one for words that start with "-" why is this?
    #pdb.set_trace()
    return wordind
    
    
        
    
