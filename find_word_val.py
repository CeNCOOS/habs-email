#
# module to take find key word or words in document and
# return the data associated with those words.  Usually it
# will be the next word.
#
import re
import numpy as np
import pdb
def find_word_val(mytext,myword,theword):
    """ def find_word_val(text,textnospace,wordtofind)
    mytext is e-mail with all spaces removed
    myword is e-mail split into "words"
    theword are the words to find
    The code returns the index of the value and the value (it is still a string)
    """
    # convert to lower case so we can be "case insensitive"
    theword=theword.lower()
    nword=theword.split()
    mytext=mytext.lower()
    #myword=myword.lower()
    lw=len(nword) # number of words that we need to find
    wordnospace=theword.replace(" ","")
    wordstart=[]
    wordstop=[]
    wordind=[]
    iflag=0
    # use the regular expression engine to find the text
    for k in re.finditer(wordnospace,mytext):
        wordstart.append(k.start())
        wordstop.append(k.end())
        iflag=1
    if iflag==0:
        # could not find word return empty list
        return [wordind, wordind]
    # found the word or phrase
    lko=np.arange(0,len(myword)) # number of words in e-mail
    lwo=np.arange(0,len(wordstart)) # number of instances of word or phrase
    for myi in lwo:
        msum=0
        for j in lko:
            msum=msum+len(myword[j])
            if int(msum) >= wordstart[myi]:
                wordind.append(j+1)
                break # we've found the string and need to break out of inner loop
    # okay we now have all the instances of the word
    lv=np.arange(0,len(wordind))
    vals=[]
    vind=[]
    # now to get the actual word and its value and return them
    for myv in lv:
        if myword[wordind[myv]].lower()==nword[0]:
            tmpv=myword[wordind[myv]+lw]
            vals.append(tmpv)
            vind.append(wordind[myv])
    return [vind, vals]
    
        
