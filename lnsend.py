#!/usr/bin/python
import sys
import httplib
import urllib
import json

#Note that this script expects that a file .lndevices exists in your home directory with 
#the contents being an array named aliases.  This is a name/value pair to associate aliases
#with api keys.  It's not required but I find it useful.
#aliases =       ["device alias",  "LiveNotify API key",
#                 "device alias2", "LiveNotify API key"]

#Read the configuration file and pull the list of devices out
def readConfigFile():
   import imp
   from os.path import expanduser
   global aliases
   
   #Open the file ~/.lndevices
   configFile = open(expanduser("~/") + ".lndevices")

   #Load the aliases variable
   temp = imp.load_source('aliases', '', configFile)

   #Store the array in the global variable for user by the script
   try:
        aliases = temp.aliases
   except AttributeError:
        aliases = ""
   configFile.close()

#Read .lndevices config file to get list of aliases
readConfigFile()

#Make sure the aliases array isn't missing entries, it contain an even number of them
if len(aliases) % 2 != 0:
   print "ERROR: The aliases array is the wrong size, it must have an even number of entries"
   sys.exit()

#Make sure we have the minimum required inputs to send a message, device + title
argumentLength = len(sys.argv) - 1
if argumentLength < 2:
   print "ERROR: At minimum you must enter a device and a title to send a notification"
   sys.exit()

#Try to match the device with a device from aliases
#if no match is found, assume they have given us an api key
device = sys.argv[1]
for alias in range(0, len(aliases), 2):
   if sys.argv[1] == aliases[alias]:
      device = aliases[alias + 1]

#get the title
title = urllib.quote_plus(sys.argv[2])

#if the argument count is high enough get
#message, url, imgurl, dest
message = ""
url = ""
imgUrl = ""
dest = "all"

if argumentLength > 2:
   message = urllib.quote_plus(sys.argv[3])
if argumentLength > 3:
   url = sys.argv[4]
if argumentLength > 4:
   imgUrl = urllib.quote_plus(sys.argv[5])
if argumentLength > 5:
   dest = sys.argv[6]

#sanitize the url so the android intent doesn't explode
#All this means is to make sure the URL starts with http://
if len(url) > 0 and not url.startswith("http://"):
   url = "http://" + url

#Escape the url
url = urllib.quote_plus(url)

#build up the query
#Argument order is
#apikey
#title
#message
#url
#imgurl
#dest (smart, phone, all) <-- this is the only parameter that can be ommited
#Remember the acronym ATM UID
httpQuery = "/notify?apikey=" + device + "&title=" + title + "&message=" + message + "&url=" + url + "&imgurl=" + imgUrl + "&dest=" + dest

#send the query
notification = httplib.HTTPConnection("api.livenotifier.net")
notification.request("GET", httpQuery)

#check and report the http status
response = json.loads(notification.getresponse().read())
if response["status"] != "OK":
    print "Failure sending notification to LiveNotify for reason: " + response["errmsg"]