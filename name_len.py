# code to move variable cruft to small file to edit
def name_len(whom):
    if whom=='Heather McNair <hmcnair72@gmail.com>':
        name=3
    if whom=='Heather McNair <heather.mcnair@lifesci.ucsb.edu>':
        name=3
    if whom=='Melissa Carter <mlcarter@ucsd.edu>':
        name=5
    if whom=='"Carter, Melissa" <mlcarter@ucsd.edu>':
        name=5
    if whom=='G. Jason':
        name=6
    if whom=='"G. Jason Smith, Ph.D." <jsmith@mlml.calstate.edu>':
        name=6
    if whom=='Kendra Negrey <khayashi@ucsc.edu>':
        name=5
    if whom=='Kendra Hayashi <khayashi@ucsc.edu>':
        name=5
    if whom=='Kelsey McBeain <kelsey.mcbeain@lifesci.ucsb.edu>':
        name=3
    if whom=='Rebecca Shipe <rshipe@gmail.com>':
        name=0 # no LOCATION listed
        # Santa Monica Pier
    if whom=='"Leandre M. Ravatt" <lravatt@calpoly.edu>':
        name=11
    if whom=='<lravatt@calpoly.edu>':
        name=11
    if whom=='Leandre Ravatt <lravatt@calpoly.edu>':
        name=11
    if whom=='Alexander Joseph Barth <ajbarth@calpoly.edu>':
        name=11
    if whom=='Jayme Smith <jaymesmi@usc.edu>':
        name=3
    if whom=='Caroline Schanche <caroline.schanche@lifesci.ucsb.edu>':
        name=3
    if whom=='Megan Nichole Wilson <mwilso36@calpoly.edu>':
        name=11
    if whom=='James Fumo <jfumo@ucsd.edu>':
        name=6
    if whom=='James T Fumo <jfumo@ucsd.edu>':
        name=5
    if whom=='Alyssa Gellene <gellene@usc.edu>':
        name=5
    return name    
