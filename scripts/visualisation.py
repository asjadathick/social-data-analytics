import analytics
from pymongo import MongoClient
import datetime
import time
import math

def calculateMeanByServiceDomain(service, serviceDomain, hoursDelta):
	iterator = 0;
	number_posts = [0, 0, 0]
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
	std_dev = math.sqrt(mean_sq_diff/len(number_posts))
	return [mean, std_dev]

	
	
[mean, stddev] = calculateMeanByServiceDomain("fb_post", "nbn", 24)
print "Mean: %(mean)d, Standard deviation: %(std_dev)d" % {"mean" : mean, "std_dev" : stddev}		
