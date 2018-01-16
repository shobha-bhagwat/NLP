from __future__ import division
import MySQLdb
import csv, time, datetime
import configparser
from configparser import ConfigParser
from datetime import date


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

conn = MySQLdb.connect(host = ConfigSectionMap("mysql")['host'], user = ConfigSectionMap("mysql")['user'], password = ConfigSectionMap("mysql")['password'], database = ConfigSectionMap("mysql")['database'])

unixtime = time.mktime(datetime.datetime.strptime(ConfigSectionMap("source")['review_date'],"%d/%m/%Y").timetuple())

cur = conn.cursor()             

try:
    cur.execute( """INSERT INTO T_WATERMARK VALUES (%(Curr_Watermark)s, %(Prev_Watermark)s, current_timestamp())""",{'Curr_Watermark':unixtime, 'Prev_Watermark':unixtime})
    conn.commit()
    print("Affected rows = {}".format(cur.rowcount))
             
except MySQLdb.IntegrityError:
        print("SQL Failed")
finally:
   conn.close()
