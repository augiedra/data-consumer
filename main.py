import requests
import datetime
import matplotlib.dates as mpldates
import matplotlib.pyplot as plt
import time
import numpy

class PricingData:
    def __init__(self, json):
        self.marketValue = json['marketValue']
        self.minBuyout = json['minBuyout']
        self.quantity = json['quantity']
        self.scannedAt = datetime.datetime.strptime(json['scannedAt'], "%Y-%m-%dT%H:%M:%S.%fZ")
        self.scannedHourly = datetime.datetime.strptime(json['scannedAt'], "%Y-%m-%dT%H:%M:%S.%fZ").replace(year=2020).replace(day=19).replace(month=1)

##############################################

class Item:

    def __init__(self, json):
        self.itemId = json['itemId']
        self.server = json['slug']
        self.pricingData = []

        # Data for matplotlib
        self.dates = []
        self.prices = []

        for data in json['data']:
            pricingData = PricingData(data)
            self.pricingData.append(pricingData)
            self.dates.append(mpldates.date2num(pricingData.scannedHourly))
            self.prices.append(pricingData.minBuyout)



##############################################

def prepareHourlyData(item):
    results = dict()
    resultCounts = dict()

    for entry in item:
        hour = entry.scannedAt.hour
        if hour in results:
            results[hour] = ((results[hour] * resultCounts[hour]) + entry.minBuyout) / (resultCounts[hour] + 1)
            resultCounts[hour] = resultCounts[hour] + 1
        else:
            print(f'First minimal buyout: {entry.minBuyout / 10000} G')
            results[hour] = entry.minBuyout
            resultCounts[hour] = 1

    return results

###############################################

def prepareWeeklyData(item):
    results = dict()
    resultCounts = dict()

    for entry in item:
        weekday = entry.scannedAt.weekday()
        if weekday in results:
            results[weekday] = ((results[weekday] * resultCounts[weekday]) + entry.minBuyout) / (resultCounts[weekday] + 1)
            resultCounts[weekday] = resultCounts[weekday] + 1
        else:
            if entry.minBuyout > 10000:
                print(f'First minimal buyout: {entry.minBuyout / 10000} G')
            elif entry.minBuyout > 100:
                print(f'First minimal buyout: {entry.minBuyout / 100} S')
            else:
                print(f'First minimal buyout: {entry.minBuyout} C')

                
            results[weekday] = entry.minBuyout
            resultCounts[weekday] = 1
    
    return results

###############################################

def drawPlot(url, dataView, color, label):
    r = requests.get(url)
    item = Item(r.json())

    if dataView == 'weekly':
        data = prepareWeeklyData(item.pricingData)
    else:
        data = prepareHourlyData(item.pricingData)

    print(f'Drawing from: {min(map(lambda x: x.scannedAt, item.pricingData))}')

    lists = sorted(data.items())
    x, y = zip(*lists)
    plt.plot(x, y, color, label=label)

def calculateMaxPriceDifference(pricingData, itemName, itemId, currentIndex, totalCount):

    print(f'{currentIndex + 1}/{totalCount}')
    if (not pricingData):
        print(f'No pricing data for {itemName}')
        return
    
    minBuyouts = []
    quantitySum = 0
    for a in pricingData:
        minBuyouts.append(a.minBuyout)
        quantitySum = quantitySum + a.quantity

    minPrice = min(minBuyouts)
    maxPrice = max(minBuyouts)
    percentIncrease = maxPrice * 100 / minPrice

    with open(f'./results/{quantitySum}___{int(round(percentIncrease)) - 100}_%___{itemName}___({itemId})', 'w') as file:
        pass

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def searchDeals():
    fileName = "./data/items4.csv" 

    fileLength = file_len(fileName)
    with open(fileName) as f:
        for i, line in enumerate(f):
            values = line.split(',')
            itemId = values[0]
            itemName = values[1].strip()
            url = f'http://localhost:3232/pricing/{itemId}/100'
            r = requests.get(url)
            item = Item(r.json())
            calculateMaxPriceDifference(item.pricingData, itemName, itemId, i, fileLength)
            # print(f'{datetime.datetime.now().minute}:{datetime.datetime.now().second}:{datetime.datetime.now().microsecond}sleeping... zzzzzzzzzzzz')
            time.sleep(0.3)
            # print(f'{datetime.datetime.now().minute}:{datetime.datetime.now().second}:{datetime.datetime.now().microsecond}waking up.... :)')

def prepareHourlyData2(item):
    results = dict()
    resultCounts = dict()

    for entry in item:
        hour = entry.scannedAt.hour
        if hour in results:
            results[hour] = ((results[hour] * resultCounts[hour]) + entry.minBuyout) / (resultCounts[hour] + 1)
            resultCounts[hour] = resultCounts[hour] + 1
        else:
            print(f'First minimal buyout: {entry.minBuyout / 10000} G')
            results[hour] = entry.minBuyout
            resultCounts[hour] = 1

    return results

def getHourlyResults(pricingData, weekday):
    hourlyResults = dict()
    hourlyResultCounts = dict()

    for data in pricingData:
        weekdayLocal = data.scannedAt.weekday()
        if weekdayLocal == weekday:
            hour = data.scannedAt.hour
            if hour in hourlyResults:
                hourlyResults[hour] = ((hourlyResults[hour] * hourlyResultCounts[hour]) + data.minBuyout) / (hourlyResultCounts[hour] + 1)
                hourlyResultCounts[hour] = hourlyResultCounts[hour] + 1
            else:
                hourlyResults[hour] = data.minBuyout
                hourlyResultCounts[hour] = 1

    return hourlyResults

def getSalesAdvice(itemId, itemName, historyLength):
    print(f'Generating advice for {itemName} ({itemId})\n')

    url = f'http://localhost:3232/pricing/{itemId}/{historyLength}'
    res = requests.get(url)
    item = Item(res.json())
    print(f'Earliest data from: {min(map(lambda x: x.scannedAt, item.pricingData))}')
    pricingData = filterPricingData(item.pricingData)

    weeklyResults = dict()
    weeklyResultCounts = dict()
    for data in pricingData:
        weekday = data.scannedAt.weekday()
        if weekday in weeklyResults:
            weeklyResults[weekday] = ((weeklyResults[weekday] * weeklyResultCounts[weekday]) + data.minBuyout) / (weeklyResultCounts[weekday] + 1)
            weeklyResultCounts[weekday] = weeklyResultCounts[weekday] + 1
        else:
            weeklyResults[weekday] = data.minBuyout
            weeklyResultCounts[weekday] = 1

    weeklyHourlyResults = dict()
    for weekday in range(0, 7):
        weeklyHourlyResults[weekday] = getHourlyResults(pricingData, weekday)

    cheapestWeekday = min(weeklyResults, key=weeklyResults.get)
    cheapestHour = min(weeklyHourlyResults[cheapestWeekday], key=weeklyHourlyResults[cheapestWeekday].get)

    expensiveWeekday = max(weeklyResults, key=weeklyResults.get)
    expensiveHour = max(weeklyHourlyResults[expensiveWeekday], key=weeklyHourlyResults[expensiveWeekday].get)

    print(f'Best time to buy: {cheapestWeekday + 1}-dienis {cheapestHour}:00. Approximate price: {weeklyHourlyResults[cheapestWeekday][cheapestHour] / 10000} G')
    print(f'Best time to sell: {expensiveWeekday + 1}-dienis {expensiveHour}:00. Approximate price: {weeklyHourlyResults[expensiveWeekday][expensiveHour] / 10000} G')


    # colors = ['-b', '-g', '-r', '-c', '-m', '-y', '-k']
    # for key, value in weeklyHourlyResults.items():
    #     print(f'{key+1}-dienis:')
    #     lists = sorted(value.items())
    #     x, y = zip(*lists)
    #     plt.plot(x, y, colors[key], f'{key+1}-dienis')

    # plt.legend(loc='best')
    # plt.show()


def filterPricingData(pricingData):
    prices = []
    for data in pricingData:
        prices.append(data.minBuyout)

    elements = numpy.array(prices)
    mean = numpy.mean(elements, axis=0)
    sd = numpy.std(elements, axis=0)

    print(f'Mean for current item is: {mean / 10000} G')
    print(f'Standard deviation for current item is: {sd / 10000} G')
    print(f'We will be removing items cheaper than {(mean - 5 * sd) / 10000} G')
    print(f'We will be removing items more expensive than {(mean + 5 * sd) / 10000} G')

    pricingDataResults = []

    for data in pricingData:
        if (data.minBuyout > mean - 5 * sd) and (data.minBuyout < mean + 5 * sd):
            pricingDataResults.append(data)
        else:
            print(f'Removing {data.minBuyout}')

    return pricingDataResults


itemId = 6049
historyLength = 40
url = f'http://localhost:3232/pricing/{itemId}/10'
url2 = f'http://localhost:3232/pricing/{itemId}/20'
url3 = f'http://localhost:3232/pricing/{itemId}/40'
url4 = f'http://localhost:3232/pricing/{itemId}/80'
url5 = f'http://localhost:3232/pricing/{itemId}/100'
url6 = f'http://localhost:3232/pricing/{itemId}/150'

# ACTIONS
###################################
# DRAW PLOTS

# drawPlot(url, 'weekly', '-b', '1')
# drawPlot(url2, 'weekly', '-g', '2')
# drawPlot(url3, 'weekly', '-r', '3')
# drawPlot(url4, 'weekly', '-c', '4')
# drawPlot(url5, 'weekly', '-m', '5')
# drawPlot(url6, 'weekly', '-y', '6')
# plt.legend(loc='best')
# plt.show()

###################################
# SCAN ALL DEALS

# searchDeals()

###################################
# SCAN ALL DEALS V2
getSalesAdvice(itemId, "testing", historyLength)