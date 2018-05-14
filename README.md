## habs-email
Python scripts to ingestion HAB sampling information from email
Vicky is excited about this!
<p>
The e-mail scraping code is read_HAB_email_to_post.py  This code has been modified to remove some of the specific urls and usernames that are specific to my implementation.  In the code it is noted where you need to place your specific url and username and password.
<p>
The code was developed using a Zimbra e-mail browser.  Some of these details may be different for your implementation.
<p>
The code uses find_plankton_word.py to find the plankton word in the e-mail payload.
<p>
The code also uses find_word_val.py to find some non-plankton values that might be important.
<p>
HABdate_to_ordinal.py converts the various date formats to python ordinal dates for plotting.
<p>
An ancillary file plankton_names.txt is a list of names that have been encountered so far in the e-mails.  It does not mean that other names might arrise in the e-mails.  It is alphabetized for easy addition of names.
<p>
The python regular expression module is used extensively to find the index of the data in the e-mail payloads.
<p>
A pickle file of the dataframes is generated for use by a NetCDF writer.  The NetCDF writer was created to try and meet Darwin Core and OBIS standards (though it is probably missing a few things at the moment).
