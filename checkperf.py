# /usr/bin/env python

summarydata = {}

with open('supervisord.log', 'r') as f:
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
for item in summarydata:
    print item
