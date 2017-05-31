import analytics
from pymongo import MongoClient
import datetime
import time
import math
from scipy import stats

def getTimeSeries(service, timeDelta, numberSteps):
	iterator = 0
	data = list()
	times = list()
	untilTime = datetime.datetime.utcnow() - datetime.timedelta(hours = 1)
	fromTime = datetime.datetime.utcnow() - datetime.timedelta(hours = (timeDelta + 1))
	while (iterator < numberSteps):
		posts = analytics.getPostsByTime(service, fromTime, untilTime)
		data.append(posts.count())
		times.append(fromTime.strftime("%d/%m/%Y %H:%M:%S (UTC)"))
		untilTime = untilTime - datetime.timedelta(hours = timeDelta)
		fromTime = fromTime - datetime.timedelta(hours = timeDelta)
		iterator += 1
	dataReturn = reversed(data)
	timesReturn = reversed(times)
	return {"data" : dataReturn, "times" : timesReturn,}


def getTotalPosts(service):
	try:
		client = MongoClient()
		db = client.test		#Maybe change this later
		datapoints = db.datapoints
	except:
		print("It appears that I can't connect to the mongodb instance, bailing out!\n")
		return(-1)
	findQuery = { 
		"source": service,
	}

	delimitQuery = {
		"_id" : "1",
	}
	posts = datapoints.find(findQuery, delimitQuery)
	return posts.count()	
	
def calculateStatsByServiceDomain(service, serviceDomain, hoursDelta):
	iterator = 0;
	number_posts = [0, 0, 0, 0, 0]
	while (iterator < len(number_posts)):
		xHoursAgo = datetime.datetime.utcnow() - datetime.timedelta(hours = (hoursDelta + (168*(iterator+1))))
		now = datetime.datetime.utcnow() - datetime.timedelta(hours = (168*(iterator+1)))
	
		xHoursAgo = datetime.datetime.utcnow() - datetime.timedelta(hours = (hoursDelta + (168*(iterator+1))))
		now = datetime.datetime.utcnow() - datetime.timedelta(hours = (168*(iterator+1)))
			#get posts related to service domains
		try:
			client = MongoClient()
			db = client.test		#Maybe change this later
			datapoints = db.datapoints
		except:
			print("It appears that I can't connect to the mongodb instance, bailing out!\n")
			return(-1)
		fromTimeStr = xHoursAgo.strftime("%Y-%m-%d %H:%M:%S")
		untilTimeStr = now.strftime("%Y-%m-%d %H:%M:%S")
		serviceDomainQuery = "associations." + serviceDomain
		
		findQuery = { 
			"source": service,
			serviceDomainQuery : True,
			"time": {
				"$gte" : fromTimeStr,
				"$lte" : untilTimeStr,
			},
		}

		delimitQuery = {
			"_id" : "1",
		}
		posts = datapoints.find(findQuery, delimitQuery)
		number_posts[iterator] = posts.count()
#		print number_posts[iterator]
		iterator = iterator + 1
		
	mean = sum(number_posts)/len(number_posts)
	mean_sq_diff = 0
	for number in number_posts:
		mean_sq_diff = mean_sq_diff + (number - mean)*(number - mean)
	std_dev = math.sqrt(mean_sq_diff/float(len(number_posts)))
	
	fromTime = datetime.datetime.utcnow() - datetime.timedelta(hours = (hoursDelta))
	fromTimeStr = fromTime.strftime("%Y-%m-%d %H:%M:%S")
	untilTimeStr = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
	
	findQuery = { 
		"source": service,
		serviceDomainQuery : True,
		"time": {
			"$gte" : fromTimeStr,
			"$lte" : untilTimeStr,
		},
	}

	delimitQuery = {
		"_id" : "1",
	}
	posts = datapoints.find(findQuery, delimitQuery)
	abs_val = posts.count()
	dev_val = (abs_val - mean)/std_dev
	
	if ((dev_val < 0.85) & (dev_val > -0.5)):
		status = "Normal"
		colour = "#c0c0c0"
	elif (dev_val >= 0.85 ):
		status = "Poor"
		colour = "#ff6600"
	else:
		status = "Good"
		colour = "#009933"
		
	probability = str((1 - stats.norm.pdf(abs_val, mean, std_dev))*100)
	probability = probability[:4]
	returnval = {
		"mean" : mean,
		"std_dev" : std_dev,
		"abs_val" : abs_val,
		"dev_val" : dev_val,
		"status" : status,
		"probability" : probability,
		"colour" : colour,
	}
	return returnval

	
	
#[mean, stddev] = calculateMeanByServiceDomain("fb_post", "nbn", 24)
#print "Mean: %(mean)d, Standard deviation: %(std_dev)d" % {"mean" : mean, "std_dev" : stddev}		
