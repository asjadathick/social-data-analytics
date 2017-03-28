import urllib2
import json
import datetime
import csv
import time
from pymongo import MongoClient

app_id = "256796421435687"
app_secret = "45ac48a47797d3e9a96c4d3249c4725b" # DO NOT SHARE WITH ANYONE!
#page_id = raw_input("Please Paste Public Page Name:")
page_id = "9322764314"

access_token = app_id + "|" + app_secret

#access_token = raw_input("Please Paste Your Access Token:")

def request_until_succeed(url):
    req = urllib2.Request(url)
    success = False
    while success is False:
        try: 
            response = urllib2.urlopen(req)
            if response.getcode() == 200:
                success = True
        except Exception, e:
            print e
            time.sleep(5)

            print "Error for URL %s: %s" % (url, datetime.datetime.now())
            print "Retrying."

    return response.read()

# Needed to write tricky unicode correctly to csv
def unicode_normalize(text):
    return text.translate({ 0x2018:0x27, 0x2019:0x27, 0x201C:0x22, 0x201D:0x22,
                            0xa0:0x20 }).encode('utf-8')

def getFacebookPageFeedData(page_id, access_token, num_statuses):

    # Construct the URL string; see http://stackoverflow.com/a/37239851 for
    # Reactions parameters

    ## Inserted code here

    twoHoursAgo = datetime.datetime.now() - datetime.timedelta(hours = 2)
    twoHoursAgoInt = int(time.mktime(twoHoursAgo.timetuple()))


    base = "https://graph.facebook.com/v2.6"
    node = "/%s/feed" % page_id 
    fields = "/?fields=message,link,permalink_url,created_time,type,name,id," + \
            "comments.limit(0).summary(true),shares,reactions" + \
            ".limit(0).summary(true)"
    parameters = "&limit=%s&since=%s&access_token=%s" % (num_statuses, twoHoursAgoInt, access_token)
    url = base + node + fields + parameters

    # retrieve data
    data = json.loads(request_until_succeed(url))
    
    return data

def getReactionsForStatus(status_id, access_token):

    # See http://stackoverflow.com/a/37239851 for Reactions parameters
        # Reactions are only accessable at a single-post endpoint

    base = "https://graph.facebook.com/v2.6"
    node = "/%s" % status_id
    reactions = "/?fields=" \
            "reactions.type(LIKE).limit(0).summary(total_count).as(like)" \
            ",reactions.type(LOVE).limit(0).summary(total_count).as(love)" \
            ",reactions.type(WOW).limit(0).summary(total_count).as(wow)" \
            ",reactions.type(HAHA).limit(0).summary(total_count).as(haha)" \
            ",reactions.type(SAD).limit(0).summary(total_count).as(sad)" \
            ",reactions.type(ANGRY).limit(0).summary(total_count).as(angry)"
    parameters = "&access_token=%s" % access_token
    url = base + node + reactions + parameters

    # retrieve data
    data = json.loads(request_until_succeed(url))
     
    return data


def processFacebookPageFeedStatus(status, access_token):

    # The status is now a Python dictionary, so for top-level items,
    # we can simply call the key.

    # Additionally, some items may not always exist,
    # so must check for existence first

    status_id = status['id']
    status_message = '' if 'message' not in status.keys() else \
            unicode_normalize(status['message'])
    link_name = '' if 'name' not in status.keys() else \
            unicode_normalize(status['name'])
    status_type = status['type']
    status_link = '' if 'link' not in status.keys() else \
            unicode_normalize(status['link'])
    status_permalink_url = '' if 'permalink_url' not in status.keys() else \
            unicode_normalize(status['permalink_url'])
    # Time needs special care since a) it's in UTC and
    # b) it's not easy to use in statistical programs.

    status_published = datetime.datetime.strptime(
            status['created_time'],'%Y-%m-%dT%H:%M:%S+0000')
    status_published = status_published.strftime(
            '%Y-%m-%d %H:%M:%S') # best time format for spreadsheet programs

    # Nested items require chaining dictionary keys.

    num_reactions = 0 if 'reactions' not in status else \
            status['reactions']['summary']['total_count']
    num_comments = 0 if 'comments' not in status else \
            status['comments']['summary']['total_count']
    num_shares = 0 if 'shares' not in status else status['shares']['count']

    # Counts of each reaction separately; good for sentiment
    # Only check for reactions if past date of implementation:
    # http://newsroom.fb.com/news/2016/02/reactions-now-available-globally/

    reactions = getReactionsForStatus(status_id, access_token) if \
            status_published > '2016-02-24 00:00:00' else {}

    num_likes = 0 if 'like' not in reactions else \
            reactions['like']['summary']['total_count']

    # Special case: Set number of Likes to Number of reactions for pre-reaction
    # statuses

    num_likes = num_reactions if status_published < '2016-02-24 00:00:00' \
            else num_likes

    def get_num_total_reactions(reaction_type, reactions):
        if reaction_type not in reactions:
            return 0
        else:
            return reactions[reaction_type]['summary']['total_count']

    num_loves = get_num_total_reactions('love', reactions)
    num_wows = get_num_total_reactions('wow', reactions)
    num_hahas = get_num_total_reactions('haha', reactions)
    num_sads = get_num_total_reactions('sad', reactions)
    num_angrys = get_num_total_reactions('angry', reactions)

    # Return a tuple of all processed data

    return (status_id, status_message, link_name, status_type, status_link, status_permalink_url,
            status_published, num_reactions, num_comments, num_shares,
            num_likes, num_loves, num_wows, num_hahas, num_sads, num_angrys)

def scrapeFacebookPageFeedStatus(page_id, access_token):
    with open('%s_facebook_statuses.csv' % page_id, 'wb') as file:
        w = csv.writer(file)
        w.writerow(["status_id", "status_message", "link_name", "status_type",
                    "status_link", "permalink_url", "status_published", "num_reactions", 
                    "num_comments", "num_shares", "num_likes", "num_loves", 
                    "num_wows", "num_hahas", "num_sads", "num_angrys"])

        has_next_page = True
        num_processed = 0   # keep a count on how many we've processed
        scrape_starttime = datetime.datetime.now()

        print "Scraping %s Facebook Page: %s\n" % (page_id, scrape_starttime)

        statuses = getFacebookPageFeedData(page_id, access_token, 100)
        # try:
        #     conn = psycopg2.connect("dbname='datachallenge_dev' user ='robot' host='localhost' password='iamarobothearmeroar!'")
        #     cur = conn.cursor()
        # except:
        #     print("Failed to open database connection, bailing out!\n")
        #     return

        try:
        	client = MongoClient()
        	db = client.test		#Maybe change this later
        	datapoints = db.datapoints
        except:
        	print("It appears that I can't connect to the mongodb instance, bailing out!\n")


        while has_next_page:
            for status in statuses['data']:

                # Ensure it is a status with the expected metadata
                if 'reactions' in status:
                    item = processFacebookPageFeedStatus(status,
                        access_token)

                    w.writerow(item)

                    #Pushing data to PostgreSQL
                    status_id = item[0]
                    status_message = item[1]
                    link_name = item[2]
                    status_type = item[3]
                    status_link = item[4]
                    permalink_url = item[5]
                    status_published = item[6]
                    num_reactions = item[7]
                    num_comments = item[8]
                    num_shares = item[9]
                    num_likes = item[10]
                    num_loves = item[11]
                    num_wows = item[12]
                    num_hahas = item[13]
                    num_sads = item[14]
                    num_angrys = item[15]



                    # query =  "INSERT INTO fb_feed (page_id, status_id, status_message, link_name, status_type, status_link, permalink_url," \
                    #          "status_published, num_reactions, num_comments, num_shares," \
                    #          " num_likes, num_loves,num_wows, num_hahas, num_sads, num_angrys) VALUES " \
                    #          "(%s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
                    # data = (page_id, status_id, status_message, link_name, status_type, status_link, permalink_url,status_published,
                    #         num_reactions, num_comments, num_shares,num_likes, num_loves,num_wows, num_hahas, num_sads, num_angrys)

                # try:
                # 	cur.execute(query, data)
                # 	conn.commit()
                # except:
                #     conn.rollback()
                #     print("Failed to write to database, attempting to roll back changes\n")

                datapoint = {
                	"source" : "fb_post",
                	"page_id" : page_id,
                	"time" : status_published,
                	"message" : status_message,
                	"likes" : num_likes,
                	"comments" : num_comments,
                	"post_id" : status_id
                }
                

                try:
                	datapoints.insert_one(datapoint)
                except:
                	print("Unable to insert into database\n")

                # output progress occasionally to make sure code is not
                # stalling
                num_processed += 1
                if num_processed % 100 == 0:
                    print "%s Statuses Processed: %s" % \
                        (num_processed, datetime.datetime.now())

            # if there is no next page, we're done.
            if 'paging' in statuses.keys():
                statuses = json.loads(request_until_succeed(
                                        statuses['paging']['next']))
            else:
                has_next_page = False


        print "\nDone!\n%s Statuses Processed in %s" % \
                (num_processed, datetime.datetime.now() - scrape_starttime)

    #conn.close()

if __name__ == '__main__':
    scrapeFacebookPageFeedStatus(page_id, access_token)
