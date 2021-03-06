from pymongo import MongoClient
import datetime
from nltk import pos_tag, word_tokenize

def unusualAnalysis(post_count, socialMediaPost):
    logfile = open('unusualLog.txt','a')
    logfile.write('============================================================\nCurrent time: ')
    logfile.write(str(datetime.datetime.now()))
    #connect to mongo
    try:
        client = MongoClient()
        db = client.test #change test to your db name
        AnalysisDailyQuar = db.AnalysisDailyQuar #change AnalysisDailyQuar to your collection name
    except:
        print("Failed to connect to AnalysisDailyQuar\n")
        return
    
    logfile.write('\nConnected to mongo\n')
    #get current quarter
    # print datetime.datetime.now()
    current_hour =  str(datetime.datetime.now()).split()[1].split(":")[0]
    # print current_hour
    current_quarter = int(current_hour)/6 + 1
    # print current_quarter
    logfile.write('Current_quarter: ')
    logfile.write(str(current_quarter))

    #get current values from mongoDB
    two_hour_avg = 0
    quarter_count = 0
    input_count = 0
    for quarter_pointer in AnalysisDailyQuar.find({"quarter":str(current_quarter)}):
        two_hour_avg = int(quarter_pointer['two_hour_avg'])
        quarter_count = int(quarter_pointer['quarter_count'])
        input_count = int(quarter_pointer['input_count'])
        # print two_hour_avg, quarter_count, input_count
    logfile.write('\nReceived values from mongoDB\n')
    logfile.write('two_hour_avg: ')
    logfile.write(str(two_hour_avg))
    logfile.write('\nquarter_count: ')
    logfile.write(str(quarter_count))
    logfile.write('\ninput_count: ')
    logfile.write(str(input_count))
        
    #check if more than two_hour_avg by 50%
    if post_count > (int(two_hour_avg)*1.5) and post_count >= (int(two_hour_avg)+10):
        logfile.write('\nSomething unusual is happening\n')
        NNP_dict = {}
        print "something unusual is happening."
        #perform NLTK
        for post in socialMediaPost:
            post_message = post['message']
            nltk_list = pos_tag(word_tokenize(post_message))
            for word in nltk_list:
                if word[1] == 'NNP':
                    key = word[0]
                    if word[1] in NNP_dict:
                        NNP_dict[key] += 1
                    else:
                        NNP_dict[key] = 1
        # print NNP_dict
        top3_NNP_words = sorted(NNP_dict, key=NNP_dict.get, reverse=True)[:3]
        print "Most used words: ", top3_NNP_words[0], top3_NNP_words[1], top3_NNP_words[2]
        logfile.write('Most used words\n')
        logfile.write(str(top3_NNP_words[0]))
        logfile.write('\n')
        logfile.write(str(top3_NNP_words[1]))
        logfile.write('\n')
        logfile.write(str(top3_NNP_words[2]))
        logfile.write('\n')
    
    logfile.write('Checked if more than two_hour_avg\n')
    #add post_count to quarter_count
    quarter_count += post_count
    logfile.write('Added post_count\n')

    #add 1 to input_count
    input_count += 1
    logfile.write('Added 1 to input_count\n')

    #recalculate two_hour_avg
    two_hour_avg = quarter_count/input_count
    logfile.write('Recalculated two_hour_avg\n')

    #update mongoDB
    AnalysisDailyQuar.update_one({"quarter":str(current_quarter)},{'$set':{"quarter_count": str(quarter_count), "two_hour_avg": str(two_hour_avg), "input_count":str(input_count)}})
    logfile.write('Updated mongoDB with values:\n')
    logfile.write('two_hour_avg: ')
    logfile.write(str(two_hour_avg))
    logfile.write('\nquarter_count: ')
    logfile.write(str(quarter_count))
    logfile.write('\ninput_count: ')
    logfile.write(str(input_count))
    
    logfile.write('\n============================================================\n')

# if __name__ == "__main__":
#     #Perform statistical analysis on data in MongoDB
#     unusualAnalysis(100, "0")
