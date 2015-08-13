# -*- coding: utf-8 -*-
"""
Created on Thu Aug 06 09:03:18 2015

@author: mdowd
"""

from bs4 import BeautifulSoup
from urllib2 import urlopen
import json
import datetime
import time
from apscheduler.scheduler import Scheduler
import logging
import pandas as pd
logging.basicConfig()
def job_function():
    collectData(routes)
    time.sleep(20)

#Pull in the Datatable    
zoneTable = pd.read_csv(r"C:\Users\MDOWD\Desktop\Blackhawk\TravelTimes\CorrectedOut_081215_V2.csv")

#####################################################
##  Functions ##
#####################################################

def collectData(route, key):
    """
    Will call a google map url and get the current google route shortname, distance, travel time, and travel time range
    it returns a tuple ('summary of info listed in previous sentence', 'full json google cached output')
    """

    outputs = []
    t = urlopen(route).read()
    start = t.find("cacheResponse(") + len("cacheResponse(")
    end = t.find("]);")+1
    tjson = t[start:end]
    j = json.loads(tjson)
    output = j[10][0][0][0]
    
    outputs.append(key[0])
    outputs.append(key[1])
    outputs.append(key[2])
    outputs.append(str(datetime.datetime.now()))
    outputs.append(output[0])
    outputs.append(output[1][1])
    outputs.append(output[6][0][1])
    
    try:
        outputs.append(output[6][4][2])
    except IndexError:
        outputs.append("NA")
    outputs.append(route)        
    print outputs

    
    return outputs, j


#This Function will print the data to a file, best used when collecting same data repeatedly
def collectDataToFile(routes):
    f = open(outfile, 'a')
    outputs = []
    for route in routes:
        t = urlopen(route).read()
        start = t.find("cacheResponse(") + len("cacheResponse(")
        end = t.find("]);")+1
        tjson = t[start:end]
        j = json.loads(tjson)
        output = j[10][0][0][0]
        outputs.append(output[0] + "," + output[6][0][1])
        #print output
        #print (datetime.datetime.now()), " , "  +  output[0] + " , " + output[6][0][1]
    outputs = [str(i) for i in outputs]
    toPrint =  str(datetime.datetime.now()) + "," + ','.join(outputs)
    print toPrint
    f.write(str(toPrint) + '\n')
    f.close()
    return j




##### To retrive the travel info for current project - Blackhawk ###
#Create three dictionaries, urlDict has the from, to, short route name and the url, we will iterate over this
#to retrive the url and call the collectData function
#outputDict will hold the expected output, so travel time, distance, etc
#rawOutputDict will hold full json output, in case there are any problems with the outputDict values

urlDict = {}
outputDict = {}
rawOutputDict = {}

#Check for urls that return more than one route, these urls return the fastest route, not the route initially selected
#when the url was copied. 
sanityDict = {}
sanityList = []
#Adjust origin and destination depending on the direction of travel
#Origin = 'Origin' for flows East, Origin = "Destination" for flows West
origin = 'Origin' 
dest =  'Destination'
theUrl = 'WestUrl' 

for row in zoneTable.iterrows():
    vals = row[1]
    urlDict[(vals[origin], vals[dest], vals['ShortName'])] = vals[theUrl]
    outputDict[(vals[origin], vals[dest], vals['ShortName'])] = []
    rawOutputDict[(vals[origin], vals[dest], vals['ShortName'])] = ''
    sanityDict[(vals[origin], vals[dest], vals['ShortName'])] = ''
    

#Populate the Dictionaries(above) with all the relevant data
cutOff = 0
for key, value in urlDict.iteritems():
    cutOff += 1
    print cutOff, key
    #CollectData returns a tuple, tuple[0] is what we want, tuple[1] is raw backup data.
    getTravelinfo = collectData(value, key)
    outputDict[key] = getTravelinfo[0]
    rawOutputDict[key] = getTravelinfo[1]
    try:
        sanityDict[key] = getTravelinfo[1][10][0][1][0]
        sanityList.append(key)
    except IndexError:
        sanityDict[key] = ''
        
#Now Convert the OutPut Data Dict into a Dataframe
toPandas = [i for i in outputDict.values()]
headers = ['Origin', 'Destination', 'ShortName', 'TimeRetr', 'Route', 'Dist', 'CurrentTime', 'TimeRange','url']
travelData = pd.DataFrame(toPandas, columns= headers)

#Adjust some column values
def extractTime(val):
    outVal = val
    if 'h' in val:
        outVal = val.split(' ')
        if len(outVal) > 2:
            outVal = 60 * int(outVal[0]) + int(outVal[2])
        else:
            outVal = 60 * int(outVal[0])
    elif 'min' in val:
        outVal = int(val.replace('min', ''))
    return outVal
    


travelData['nDist'] = (travelData.Dist.apply(lambda x: x[0:4])).astype(float)
travelData['nTime'] = (travelData.CurrentTime.apply(lambda x: extractTime(x))) 
travelData = travelData.sort(["Origin", "Destination"])

#################
##Below if we are doing repeated capture
#################
def startCapture():
    # Start the scheduler
    sched = Scheduler()
    sched.daemonic = False
    sched.start()
    print datetime.datetime.now()
    # Schedules job_function to be run once each minute
    #sched.add_cron_job(job_function,  minute='0-59')
    sched.add_interval_job(job_function, minutes=10)
