#!/usr/bin/env python -x
import sys

summarydata = {}

with open( sys.argv[1], 'r') as f:
    for line in f:
        if 'generated' in line:
            mydata = line.split(']')
            datapoints = mydata[2].split(' ')
            key = datapoints[1]+':'+datapoints[2]
            timing = int(datapoints[8])
            if key in summarydata:
                currentdata = summarydata[key]
                if currentdata['max'] < timing:
                    currentdata['max'] = timing
                if currentdata['min'] > timing:
                    currentdata['min'] = timing
                currentdata['total'] += timing
                currentdata['count'] += 1
            else:
                summarydata[key] = {
                    'min': timing,
                    'max': timing,
                    'total': timing,
                    'count': 1}

summarydata =  sorted(summarydata.items(), key=lambda item: item[1]['max'], reverse=True)
for i in range(0,10):
    url, data = summarydata[i]
    print url
    print '------------------------------------------------'
    print 'max : ' + str(data['max']) + '\tavg: ' + str(data['total'] / data['count']) + '\tmin: ' + str(data['min']) + '\tHits: ' + str(data['count'])
    print '------------------------------------------------'
