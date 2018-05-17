INTRODUCTION

	This project contains all the code necessary to run the script email_func to achieve the mentioned functionality

	This code is built using Python Windows IDLE for Python 3.6.0

INITIALIZATION

In order to setup the necessary code base for running the script, following steps need to be executed-

1. Run the DDL dump 
2. Setup the config.ini and update the following and also any other parameters if needed -
	a. host, database, user, password for MySQL database connection
	b. Update the url under [source] section to set the "start" to the date from when the reviews should be processed
	c. Update the url under [source] section to set the "res_id" to appropriate value for the desired restaurant ("Tabla" restaurant in Bangalore is used as an example here)
	d. Update the user_key under [source] section as necessary
	e. Update the review_date under [source] section to the date (in dd/mm/yyyy format) from when the reviews should be processed 
	f. Update the file paths under [file_path] section if the said files have been copied to any other location
3. Copy the config.ini file to local directory and change its path in init.py and email_func.py under "Config.read('C:\\Users\\home\\Dropbox\\config.ini')"
4. Run init.py to initialize the Watermark table


INSTRUCTIONS

In order to schedule the script, run scheduler.py

