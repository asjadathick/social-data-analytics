from pymongo import MongoClient

def statisticAnalysis():
    #connect to mongo
    try:
        client = MongoClient()
        db = client.test #change test to your db name
        collection = db.datapoints #change datapoints to your collection name
    except:
        print("Failed to connect to mongoDB\n")
        return

    #===================================
    #Prints the number of posts grouped by date
    #===================================
    date = []
    date_posts_count = []
    date_posts_two_hour_count = []
    for post in collection.find():
        current_post_date = post['time'].split()[0]
        current_post_time = int(post['time'].split()[1][0:2])//2
        if current_post_date in date:
            date_posts_count[date.index(current_post_date)] += 1
            date_posts_two_hour_count[date.index(current_post_date)][current_post_time] += 1
        else:
            date.append(current_post_date)
            date_posts_count.append(1)
            date_posts_two_hour_count.append([0,0,0,0,0,0,0,0,0,0,0,0])
            date_posts_two_hour_count[-1][current_post_time] = 1

    for i in range (len(date)):
        print ("Date: %s\nNumber of posts: %s\n" % (date[i],date_posts_count[i]))

    #===================================
    #Statistical analysis
    #===================================
    total_post = 0
    for item in date_posts_count:
        total_post += item
    print "Total post: ", total_post
    print "Number of days: ", len(date)

    #calculate average number of post per day
    daily_avg = total_post/len(date_posts_count)
    print "Average numnber of post per day: ", daily_avg

    #calculate average number of post per 2 hour from 12am to 6am
    temp = 0
    for i in range (len(date_posts_two_hour_count)):
        for j in range (0,3):
            temp += date_posts_two_hour_count[i][j]
    avg_1 = temp / (len(date_posts_two_hour_count)*3)
    print "Average number of post per 2 hour from 12am to 6am: ", avg_1

    #calculate average number of post per 2 hour from 6am to 12pm
    temp = 0
    for i in range (len(date_posts_two_hour_count)):
        for j in range (3,6):
            temp += date_posts_two_hour_count[i][j]
    avg_2 = temp / (len(date_posts_two_hour_count)*3)
    print "Average number of post per 2 hour from 6am to 12pm: ", avg_2

    #calculate average number of post per 2 hour from 12pm to 6pm
    temp = 0
    for i in range (len(date_posts_two_hour_count)):
        for j in range (6,9):
            temp += date_posts_two_hour_count[i][j]
    avg_3 = temp / (len(date_posts_two_hour_count)*3)
    print "Average number of post per 2 hour from 12pm to 6pm: ", avg_3

    #calculate average number of post per 2 hour from 6pm to 12am
    temp = 0
    for i in range (len(date_posts_two_hour_count)):
        for j in range (9,12):
            temp += date_posts_two_hour_count[i][j]
    avg_4 = temp / (len(date_posts_two_hour_count)*3)
    print "Average number of post per 2 hour from 6pm to 12am: ", avg_4

    #calculate vairance and standard deviation
    variance = 0
    for item in date_posts_count:
        variance += (item - daily_avg)**2
    variance  = variance/len(date_posts_count)
    std_deviation = variance**0.5
    print "Daily posts vairance: ", variance
    print "Daily posts standard deviation: ", std_deviation

if __name__ == "__main__":
    #Perform statistical analysis on data in MongoDB
    statisticAnalysis()
