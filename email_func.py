#! /usr/bin/env python

from __future__ import division
import MySQLdb
import urllib.request
import csv, time, datetime
import requests, json, configparser
from string import punctuation
import sendgrid
import os
from sendgrid.helpers.mail import *
from configparser import ConfigParser

def main():
    CUR_TIME = time.time()

    # Function to read config file
    def ConfigSectionMap(section):
        dict1 = {}
        Config = ConfigParser()
        Config.read('C:\\Users\\home\\Dropbox\\config.ini')
        options = Config.options(section)
        for option in options:
            try:
                dict1[option] = Config.get(section, option)
                if dict1[option] == -1:
                    DebugPrint("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                dict1[option] = None
        return dict1

    url = ConfigSectionMap("source")['url']  #URL of zomato API
    user_key =ConfigSectionMap("source")['user_key']
    headers = {'content-type': 'application/json', 'user-key': user_key }
    r = requests.get(url, headers=headers)
    data = r.json()
    count = 0
    tot_cnt = 0
    neg_cnt = 0
    Email_flag = 1
    neg_reviews = { "user_review":[]}
    prev_w = ''
    pw = ''
    timest = 0
    flag = 0

    conn = MySQLdb.connect(host = ConfigSectionMap("mysql")['host'], user = ConfigSectionMap("mysql")['user'], password = ConfigSectionMap("mysql")['password'], database = ConfigSectionMap("mysql")['database'])

    cur = conn.cursor()
    cur.execute( "SELECT Curr_Watermark FROM T_WATERMARK" )  #Retrieve the datetime from last time the process was successfully run
    timest = int(cur.fetchone()[0])


    #Function to read positive words, negative words dictionaries etc
    def read_file(path):
        u = urllib.request.urlopen(path)
        data = u.read()
        u.close()
        with open('path_file.txt', "wb") as f :
            f.write(data)
        data_sent = open('path_file.txt').read()
        data_words = data_sent.split('\n')
        return data_words

    
    positive_words = read_file(ConfigSectionMap("file_path")['path_pos'])
    negative_words = read_file(ConfigSectionMap("file_path")['path_neg'])
    incrementers = read_file(ConfigSectionMap("file_path")['path_inc'])
    decrementers = read_file(ConfigSectionMap("file_path")['path_dec'])
    inverters = read_file(ConfigSectionMap("file_path")['path_inv'])


    #Process the output of Zomato API Call
    for i in data['user_reviews']:
        if data['user_reviews'][count]['review']['timestamp'] <= timest:
            count = count + 1                # This counter acts as index for dictionary returned in the Zomato API
            continue                         # Ignore the reviews which had already been processed

        rating = data['user_reviews'][count]['review']['rating']

        if rating < 4.5:
    
            rvw = data['user_reviews'][count]['review']['review_text']
            word_list = rvw.split('\n')         #Split the sentences in the review text
            positive_counter=0
            negative_counter=0

            for word in word_list:
    
                word_processed = word.lower()                           

                word_processed = word_processed.replace('n\'t',' not')   #Replace n't to not in review text for better sentiment analysis result

                for p in list(punctuation):
                    word_processed = word_processed.replace(p,' ')

                words = word_processed.split(' ')                       

                word_count=len(words)
            
                for w in words:                 #Basic sentiment analysis
                
                    if w in positive_words:
                        if prev_w in incrementers:                      #If current word is preceeded by 'very' etc. increase the positive point
                            positive_counter = positive_counter + 1.5
                        elif prev_w in decrementers:
                            positive_counter = positive_counter + 0.5           #If current word is preceeded by 'barely' etc. decrease the positive point
                        elif prev_w in inverters or pw+' '+prev_w in inverters:
                            negative_counter = negative_counter + 1              #If current word is preceeded by 'not' etc. change polarity
                        else:
                            positive_counter = positive_counter + 1
                        
                    elif w in negative_words:
                        if prev_w in incrementers:
                            negative_counter = negative_counter + 1.5
                        elif prev_w in decrementers:
                            negative_counter = negative_counter + 0.5
                        elif prev_w in inverters or pw+' '+prev_w in inverters:
                            positive_counter = positive_counter + 1
                        else:
                            negative_counter = negative_counter + 1
                
                    pw = prev_w                                     # Word 2 back than current word, to check for words like ""
                    prev_w = w                                      # Previous word to check for incrementers, decrementers & inverters

                
            positive_per = (positive_counter/(positive_counter + negative_counter))*100  #Positive percentage among the adjectives/adverbs considered

            if positive_per < 75:
                 neg_cnt = neg_cnt + 1
                 review = {}
                 review['rating'] = data['user_reviews'][count]['review']['rating']
                 review['timestamp'] = data['user_reviews'][count]['review']['timestamp']
                 review['review'] = data['user_reviews'][count]['review']['review_text']

                 neg_reviews["user_review"].append(review)   #dict to capture negative reviews from the overall list of reviews
                 flag = 1

    
        tot_cnt = tot_cnt + 1
        count = count + 1
    

    cnt = len(neg_reviews)

    c = 0   #counter for index

    if flag == 1:

        for c in range(0,cnt):          # This code is to manipulate new_reviews appropriately for including in mail body
            user_rvw = {}
            user_rvw['Rating'] = neg_reviews['user_review'][c]['rating']
            user_rvw['Time'] = datetime.datetime.fromtimestamp(int(neg_reviews['user_review'][c]['timestamp'])).strftime('%Y-%m-%d %I:%M:%S %p %Z')
            user_rvw['Review'] = neg_reviews['user_review'][c]['review']

            with open('log.txt','w') as log:
                [log.write("Below are the negative reviews:\n\n")]
                [log.write("%s: %s\n\n" % (key,value)) for key, value in user_rvw.items()]
                [log.write("\n\nTotal reviews processed: %s\n\n Positive review count: %s\n\n  Negative review count: %s\n\n" % (tot_cnt,neg_cnt,tot_cnt-neg_cnt))]


        sg = sendgrid.SendGridAPIClient(apikey=ConfigSectionMap("mail")['api_key'])
        from_email = Email(ConfigSectionMap("mail")['from_email'])
        subject = "Received negative review on Zomato"
        to_email = Email(ConfigSectionMap("mail")['to_email'])
        content = Content("text/plain", str(open('log.txt', 'r').read()))
        mail = Mail(from_email, subject, to_email, content)

        response = sg.client.mail.send.post(request_body=mail.get())

        if response.status_code != 202:
           print('An error occurred: {}'.format(response.body), 500)
           Email_flag = 0


    cur = conn.cursor()             #Updating database log and watermark tables

    try:
        cur.execute( """INSERT INTO T_PROCESS_LOG(Review_Count, Negative_Count, Positive_Count, Email_Sent_Flag, Processed_At) VALUES (%(Review_Count)s, %(Negative_Count)s, %(Positive_Count)s, %(Email_Sent_Flag)s, current_timestamp())""",{'Review_Count':tot_cnt, 'Negative_Count':neg_cnt, 'Positive_Count':tot_cnt-neg_cnt, 'Email_Sent_Flag':Email_flag})
        conn.commit()
        print("Affected rows = {}".format(cur.rowcount))

        if cur.rowcount ==1:
            cur.execute( """UPDATE T_WATERMARK SET Prev_Watermark = Curr_Watermark, Curr_Watermark = %(Curr_Watermark)s, Updated_At = current_timestamp()""",{'Curr_Watermark':CUR_TIME})
            conn.commit()
            print("Affected rows for update = {}".format(cur.rowcount))
             
    except MySQLdb.IntegrityError:
            print("DML Failed")
    finally:
       conn.close()

if __name__ == "__main__":
    main()
