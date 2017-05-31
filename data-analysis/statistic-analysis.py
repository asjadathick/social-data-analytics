from pymongo import MongoClient
import matplotlib.pyplot as plt
import datetime
import matplotlib

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

    date_posts_count = {}
    date_posts_two_hour_count = {}

    for post in collection.find():
        current_post_date = post['time'].split()[0]
        current_post_time = int(post['time'].split()[1][0:2])//2
        if current_post_date in date_posts_count:
            date_posts_count[current_post_date] += 1
            date_posts_two_hour_count[current_post_date][current_post_time] += 1
        else:
            date_posts_count[current_post_date] = 1
            date_posts_two_hour_count[current_post_date] = [0,0,0,0,0,0,0,0,0,0,0,0]
            date_posts_two_hour_count[current_post_date][current_post_time] += 1

    for date in date_posts_count:
        print ("Date: %s\nNumber of posts: %s\n" % (date,date_posts_count[date]))

    #===================================
    #Statistical analysis
    #===================================
    total_post = 0
    for date in date_posts_count:
        total_post += date_posts_count[date]
    print "Total post: ", total_post
    print "Number of days: ", len(date_posts_count)

    #calculate average number of post per day
    daily_avg = total_post/len(date_posts_count)
    print "Average numnber of post per day: ", daily_avg

    #calculate average number of post per 2 hour from 12am to 6am
    temp = 0
    for date in date_posts_two_hour_count:
        for j in range (0,3):
            temp += date_posts_two_hour_count[date][j]
    avg_1 = temp / (len(date_posts_two_hour_count)*3)
    print "Average number of post per 2 hour from 12am to 6am: ", avg_1

    #calculate average number of post per 2 hour from 6am to 12pm
    temp = 0
    for date in date_posts_two_hour_count:
        for j in range (3,6):
            temp += date_posts_two_hour_count[date][j]
    avg_2 = temp / (len(date_posts_two_hour_count)*3)
    print "Average number of post per 2 hour from 6am to 12pm: ", avg_2

    #calculate average number of post per 2 hour from 12pm to 6pm
    temp = 0
    for date in date_posts_two_hour_count:
        for j in range (6,9):
            temp += date_posts_two_hour_count[date][j]
    avg_3 = temp / (len(date_posts_two_hour_count)*3)
    print "Average number of post per 2 hour from 12pm to 6pm: ", avg_3

    #calculate average number of post per 2 hour from 6pm to 12am
    temp = 0
    for date in date_posts_two_hour_count:
        for j in range (9,12):
            temp += date_posts_two_hour_count[date][j]
    avg_4 = temp / (len(date_posts_two_hour_count)*3)
    print "Average number of post per 2 hour from 6pm to 12am: ", avg_4

    #calculate vairance and standard deviation
    variance = 0
    for date in date_posts_count:
        variance += (date_posts_count[date] - daily_avg)**2
    variance  = variance/len(date_posts_count)
    std_deviation = variance**0.5
    print "Daily posts vairance: ", variance
    print "Daily posts standard deviation: ", std_deviation

    #===================================
    #Visualization on date_posts_count
    #===================================

    #Preparing the elements for x and y
    dates_in_string = []
    for date in date_posts_count:
        dates_in_string.append(date)
    dates_datetime = []
    postsVsDate_list = []
    for d in dates_in_string:
        dates_datetime.append(datetime.datetime.strptime(d, '%Y-%m-%d'))
        postsVsDate_list.append(date_posts_count[d])
    dates_float = matplotlib.dates.date2num(dates_datetime)

    #sorting the x axis
    z = sorted(zip(dates_float,postsVsDate_list))
    dates_float=[i[0] for i in z]
    postsVsDate_list=[i[1] for i in z]

    #plotting the data
    plt.xlabel("Date")
    plt.ylabel("Number of posts")
    plt.title("Number of posts against date")
    plt.plot_date(dates_float, postsVsDate_list, linestyle='-', xdate=True, ydate=False)
    plt.show()


    #===================================
    #Visualization on average number of posts every quarter
    #===================================
    #Preparing the frames for plots
    fig = plt.figure()
    ax1 = fig.add_subplot(221)
    plt.xlabel("Date")
    plt.ylabel("Number of posts")
    plt.title("Average posts from 12am to 6am")
    ax2 = fig.add_subplot(222)
    plt.xlabel("Date")
    plt.ylabel("Number of posts")
    plt.title("Average posts from 6am to 12pm")
    ax3 = fig.add_subplot(223)
    plt.xlabel("Date")
    plt.ylabel("Number of posts")
    plt.title("Average posts from 12pm to 6pm")
    ax4 = fig.add_subplot(224)
    plt.xlabel("Date")
    plt.ylabel("Number of posts")
    plt.title("Average posts from 6pm to 12am")

    #===================================
    #Visualization on average number of posts between 12am to 6am
    #===================================
    #Preparing the elements for x and y
    dates_in_string = []
    for date in date_posts_count:
        dates_in_string.append(date)
    dates_datetime = []
    for d in dates_in_string:
        dates_datetime.append(datetime.datetime.strptime(d, '%Y-%m-%d'))
    dates_float = matplotlib.dates.date2num(dates_datetime)

    avg_posts_12a_6a = []
    for date in date_posts_two_hour_count:
        temp = 0
        for j in range (0,3):
            temp += date_posts_two_hour_count[date][j]
        avg_posts_12a_6a.append(temp/3)

    #sorting the x axis
    z = sorted(zip(dates_float,avg_posts_12a_6a))
    dates_float=[i[0] for i in z]
    avg_posts_12a_6a=[i[1] for i in z]

    #plotting the data
    ax1.plot_date(dates_float, avg_posts_12a_6a, linestyle='-', xdate=True, ydate=False)


    #===================================
    #Visualization on average number of posts between 6am to 12pm
    #===================================

    #Preparing the elements for x and y
    dates_in_string = []
    for date in date_posts_count:
        dates_in_string.append(date)
    dates_datetime = []
    for d in dates_in_string:
        dates_datetime.append(datetime.datetime.strptime(d, '%Y-%m-%d'))
    dates_float = matplotlib.dates.date2num(dates_datetime)

    avg_posts_6a_12p = []
    for date in date_posts_two_hour_count:
        temp = 0
        for j in range (3,6):
            temp += date_posts_two_hour_count[date][j]
        avg_posts_6a_12p.append(temp/3)

    #sorting the x axis
    z = sorted(zip(dates_float,avg_posts_6a_12p))
    dates_float=[i[0] for i in z]
    avg_posts_6a_12p=[i[1] for i in z]

    #plotting the data
    ax2.plot_date(dates_float, avg_posts_6a_12p, linestyle='-', xdate=True, ydate=False)

    #===================================
    #Visualization on average number of posts between 12pm to 6pm
    #===================================

    #Preparing the elements for x and y
    dates_in_string = []
    for date in date_posts_count:
        dates_in_string.append(date)
    dates_datetime = []
    for d in dates_in_string:
        dates_datetime.append(datetime.datetime.strptime(d, '%Y-%m-%d'))
    dates_float = matplotlib.dates.date2num(dates_datetime)

    avg_posts_12p_6p = []
    for date in date_posts_two_hour_count:
        temp = 0
        for j in range (6,9):
            temp += date_posts_two_hour_count[date][j]
        avg_posts_12p_6p.append(temp/3)

    #sorting the x axis
    z = sorted(zip(dates_float,avg_posts_12p_6p))
    dates_float=[i[0] for i in z]
    avg_posts_12p_6p=[i[1] for i in z]

    #plotting the data
    ax3.plot_date(dates_float, avg_posts_12p_6p, linestyle='-', xdate=True, ydate=False)

    #===================================
    #Visualization on average number of posts between 6pam to 12am
    #===================================

    #Preparing the elements for x and y
    dates_in_string = []
    for date in date_posts_count:
        dates_in_string.append(date)
    dates_datetime = []
    for d in dates_in_string:
        dates_datetime.append(datetime.datetime.strptime(d, '%Y-%m-%d'))
    dates_float = matplotlib.dates.date2num(dates_datetime)

    avg_posts_6p_12a = []
    for date in date_posts_two_hour_count:
        temp = 0
        for j in range (0,3):
            temp += date_posts_two_hour_count[date][j]
        avg_posts_6p_12a.append(temp/3)

    #sorting the x axis
    z = sorted(zip(dates_float,avg_posts_6p_12a))
    dates_float=[i[0] for i in z]
    avg_posts_6p_12a=[i[1] for i in z]

    #plotting the data
    ax4.plot_date(dates_float, avg_posts_6p_12a, linestyle='-', xdate=True, ydate=False)
    plt.show()


if __name__ == "__main__":
    #Perform statistical analysis on data in MongoDB
    statisticAnalysis()
