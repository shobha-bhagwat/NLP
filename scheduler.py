#!/usr/bin/env python
 
from datetime import datetime
import sys
from time import sleep
import os
import subprocess
from apscheduler.schedulers.background import BackgroundScheduler
import email_func


def my_job():
    email_func.main()


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(my_job, 'interval', minutes=60)
    scheduler.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        while True:
            sleep(300)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
