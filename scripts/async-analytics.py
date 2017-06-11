from pymongo import MongoClient
import analytics
import unusualAnalysis
import datetime
import os
import csv

def updateDomainAssociation(documentID, associations):
	try:
		client = MongoClient()
		db = client.test		#Maybe change this later
		datapoints = db.datapoints
	except:
		print("It appears that I can't connect to the mongodb instance, bailing out (updateDomainAssociation)!\n")
		return(-1)
	
	query = {"_id" : documentID}
	changed = {"$set" : {"associations" : associations}}
	
	datapoints.update(query, changed, upsert=False)

def domainAssociation(service, fromTime):
	wordset = {
		"nbn" : ['nbn', 'quigley', 'fttn', 'fttp'],
		"foxtel" : ['cable', 'foxtel', 'channel'],
		"bigpond" : [['internet', 'service'], 'net', 'broadband', 'adsl', 'adsl2+', 'adsl2', 'internet', 'cable', 'bigpond', 'mbps', 'kbps', 'dialup', 'modem', 'dongle'],
		"customer_service" : ['account', 'complaint', 'complaints', 'sales', 'filipino', 'indian', 'accent', 'call', 'hold', 'callcentre', 'philippines', 'india', 'centre', 'store', 'bill', 'invoice', 'bills', 'invoices', 'indians', 'filipinos', 'order', 'support', 'billing', 'chat', '24x7', 'consultant', 'manager'],
		"mobile" : ['sim', 'simcard', 'data', 'text', 'roaming', '4g', '3g', '2g', 'LTE', 'mobile', 'cell', 'cellphone', 'txt', 'sms', 'gprs', 'tower', 'reception', 'mobiles',  'blackspot', 'signal',],
		"pots" : ['landline', ['land', 'line'], 'land']
	}
	associations = {
		"nbn" : False,
		"foxtel" : False,
		"bigpond" : False,
		"mobile" : False,
		"pots" : False,
		"customer_service" : False,
	
	}
	
	try:
		os.remove("results.csv")
	except:
		print("\nNo existing file to delete\n")

	# with open("results.csv", "w") as csvFile:
		# csvWriter = csv.writer(csvFile)
		# csvWriter.writerow(["Status ID", "Date/Time", "Message", "nbn", "foxtel", "bigpond", "mobile", "POTS", "customer_service"])
	
	posts = analytics.getPostsByTime(service, fromTime, datetime.datetime.utcnow())
	print "There have been %(num_posts)s posts to %(service)s since the epoch at %(epoch)s" % \
		{"num_posts" : posts.count(), "epoch" : fromTime.strftime("%Y-%m-%d %H:%M:%S"), "service" : service}
	#======================================
	#Adding unusualAnalysis that reports on anything unusual
	try:
		unusualAnalysis(posts.count(), posts)
	except:
		print "Error in unusual Analysis. Report to Kevin"
	#======================================	
	for post in posts:
		words = analytics.naturalLangProc(post['_id'])
		for word in words:
			for key in wordset:
				if word in wordset[key]:
					associations[key] = True
		updateDomainAssociation(post['_id'], associations)
		# with open("results.csv", "a") as csvFile:
			# csvWriter = csv.writer(csvFile)
			# csvWriter.writerow([post['post_id'].encode('utf-8'), post['time'].encode('utf-8'), post['message'].encode('utf-8'), associations['nbn'], associations['foxtel'], associations['bigpond'], associations['mobile'], associations['pots'], associations['customer_service']])
		associations = {
			"nbn" : False,
			"foxtel" : False,
			"bigpond" : False,
			"mobile" : False,
			"pots" : False,
			"customer_service" : False,
		}

			

twoHoursAgo = datetime.datetime.utcnow() - datetime.timedelta(hours = 2)
#epochDateTime = analytics.findEpoch("fb_post")	
domainAssociation("fb_post", twoHoursAgo)
