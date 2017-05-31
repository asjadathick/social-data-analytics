from pymongo import MongoClient
import pymongo as pmongo
import datetime
import time
import csv
import os
import re
import nltk
import math
import scipy.stats as stats

def getPostsByTime(service, fromTime, untilTime):
# Returns a MongoClient cursor object filled with 
	try:
		client = MongoClient()
		db = client.test		#Maybe change this later
		datapoints = db.datapoints
	except:
		print("It appears that I can't connect to the mongodb instance, bailing out!\n")
		return(-1)

	fromTimeStr = fromTime.strftime("%Y-%m-%d %H:%M:%S")
	untilTimeStr = untilTime.strftime("%Y-%m-%d %H:%M:%S")

	findQuery = { 
		"source": service,
		"time": {
			"$gte" : fromTimeStr,
			"$lte" : untilTimeStr
		}
	}

	delimitQuery = {
		"_id" : "1",
		"post_id" : "1",
		"time" : "1",
		"message" : "1"
	}


	return(datapoints.find(findQuery, delimitQuery))
	
def calculateMean(service, hoursDelta):
	iterator = 0;
	number_posts = [0, 0, 0]
	while (iterator < len(number_posts)):
		xHoursAgo = datetime.datetime.utcnow() - datetime.timedelta(hours = (hoursDelta + (168*(iterator+1))))
		now = datetime.datetime.utcnow() - datetime.timedelta(hours = (168*(iterator+1)))
		posts = getPostsByTime(service, xHoursAgo, now)
		number_posts[iterator] = posts.count()
#		print number_posts[iterator]
		iterator = iterator + 1
	mean = sum(number_posts)/len(number_posts)
	mean_sq_diff = 0
	for number in number_posts:
		mean_sq_diff = mean_sq_diff + (number - mean)*(number - mean)
	std_dev = math.sqrt(mean_sq_diff/len(number_posts))
	return [mean, std_dev]
	
def calculateDeviation(service, hoursDelta):
	[mean, std_dev] = calculateMean(service, hoursDelta)
	xHoursAgo = datetime.datetime.utcnow() - datetime.timedelta(hours = (hoursDelta))
	now = datetime.datetime.utcnow()
	posts = getPostsByTime(service, xHoursAgo, now)
	current_num = posts.count()
	dev = (current_num - mean)/std_dev
	distribution = stats.norm(mean, std_dev)
	if dev > 0:
		print "Result is %(dev)f standard deviations above the 4 week mean.\n" % { "dev" : dev}
		print "There is a %(perc)f percent chance that this is due to normal variations" % {"perc" : (distribution.cdf(current_num)) * 100}
	else:
		pprint("Result is %s deviations below the 4 week mean.", dev)

def findEpoch(service):
#Returns the time of the first post in the database from the service specified
	try:
		client = MongoClient()
		db = client.test		#Maybe change this later
		datapoints = db.datapoints
	except:
		print("It appears that I can't connect to the mongodb instance, bailing out!\n")
		return(-1)
	findQuery = { "source": service }
	delimitQuery = { "time" : "1" }
	dps = datapoints.find(findQuery, delimitQuery).sort("time", pmongo.ASCENDING)
	return datetime.datetime.strptime(dps[0]['time'], "%Y-%m-%d %H:%M:%S")
	
	
	
	
	
	
def getPostByID(postID):
	try:
		client = MongoClient()
		db = client.test		#Maybe change this later
		datapoints = db.datapoints
	except:
		print("It appears that I can't connect to the mongodb instance, bailing out!\n")
		return(-1)

	datapoint = datapoints.find_one({"_id" : postID})
	#random comment
	return datapoint


def naturalLangProc(postID):
	#Get post from non-relational storage
	datapoint = getPostByID(postID)
	assert (datapoint != (-1))
	#Pre-processing:
	#Remove all punctuation using a regular expression
	letters_only = re.sub("[^a-zA-Z]", " ", datapoint['message']) 
	#Change everything to lower case
	lower_case = letters_only.lower()
	words = lower_case.split()
	stops = set(nltk.corpus.stopwords.words("english"))
	words = [w for w in words if not w in stops]
	return words

findEpoch("fb_post")


# oneDayAgo = datetime.datetime.utcnow() - datetime.timedelta(hours = 24)
# oneWeekAgo = datetime.datetime.utcnow() - datetime.timedelta(days = 7)
# oneDayAndAWeekAgo = oneDayAgo - datetime.timedelta(days = 7)

# results = getPostsByTime("fb_post", oneDayAgo, datetime.datetime.utcnow())
# last24Hours = results.count()
# results = getPostsByTime("fb_post", oneDayAndAWeekAgo, oneWeekAgo)
# thisTimeLastWeek = results.count()

# for result in results:
	# naturalLangProc(result['_id'])

# print last24Hours, " posts in previous 24 hours, compared to ", thisTimeLastWeek, " for the same period last week."


# try:
# 	os.remove("results.csv")
# except:
# 	print("\nNo existing file to delete\n")

# with open("results.csv", "w") as csvFile:
# 	csvWriter = csv.writer(csvFile)
# 	csvWriter.writerow(["Status ID", "Date/Time", "Message"])
# 	for result in results:
# 		csvWriter.writerow([result['post_id'].encode('utf-8'), result['time'].encode('utf-8'), result['message'].encode('utf-8')])



