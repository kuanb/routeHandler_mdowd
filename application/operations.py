from urllib2 import urlopen
import requests
import json
import datetime
import time
import pandas as pd



def runTest(fileName):
    print fileName
    return 'this is result' + fileName


def runRoutes(fileName):

    zoneTable = pd.read_csv(fileName)

    urlDict = {}
    outputDict = {}
    rawOutputDict = {}

    sanityDict = {}
    sanityList = []

    origin = 'Origin' 
    dest = 'Destination'
    theUrl = 'WestUrl' 



    for row in zoneTable.iterrows():

        vals = row[1]
        urlKey = (vals[origin], vals[dest], vals['ShortName']) ## why are they key values being constructed like this? seems dangerous

        urlDict[urlKey] = vals[theUrl]
        
        # are these necessary? you override them in the following for loop
        outputDict[urlKey] = []
        rawOutputDict[urlKey] = ''
        sanityDict[urlKey] = ''
        


    for key, route in urlDict.iteritems():
        
        # this method returns Google LiteMaps query result (no info about browser is why)
        # response = urlopen(route).read()
        response = requests.get(route).text
        
        # risky (esp 'end') since you are assuming that you'll get that common phrase somewhere else, would make more "specific"
        start = response.find('cacheResponse(') + len('cacheResponse(')
        end = response.find(']);')+1 

        try:
            cleaned = json.loads(response[start:end])
            output = cleaned[10][0][0][0]
            
            currTime = str(datetime.datetime.now())
            travelInfo = [key[0], key[1], key[2], currTime, output[0], output[1][1], output[6][0][1]]
            
            try:
                travelInfo.append(output[6][4][2])
            except IndexError:
                travelInfo.append('NA')

            travelInfo.append(route)        

            outputDict[key] = travelInfo
            rawOutputDict[key] = output

            try:
                sanityDict[key] = output[1][10][0][1][0]
                sanityList.append(key)
            except (IndexError, TypeError) as e:
                sanityDict[key] = ''

        except ValueError:
            failed = True
            print 'Failed to get correct HTML response from Google.'


    if not failed:
        toPandas = [i for i in outputDict.values()]
        headers = ['Origin', 'Destination', 'ShortName', 'TimeRetr', 'Route', 'Dist', 'CurrentTime', 'TimeRange','url']
        travelData = pd.DataFrame(toPandas, columns= headers)



        def produceTime(val):
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
        travelData['nTime'] = (travelData.CurrentTime.apply(lambda x: produceTime(x)))

        travelData = travelData.sort(["Origin", "Destination"])


        travelData.to_csv('output.csv', sep=',', encoding='utf-8')
