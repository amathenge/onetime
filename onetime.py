# functions to implement a onetime pin (OTP).
# The idea is to:
#   look up the OTP in a database for the user
#   the db has the following fields:
#       id -> integer primary key autoincrement
#       userid -> integer - id of user (from users table)
#       otp -> varchar(6) - the valid OTP that was sent to the user
#       otp_time -> datetime - the time that the OTP was sent
#       valid -> boolean - flag indicating if the OTP is valid
#
# The structure of the user table will depend on the application, but it's important that the
# the USERID is consistent.
#
import sqlite3
from datetime import datetime, timedelta
import math
import random

# some stuff that needs to be set up
otp_db = 'onetime.db'

# create a one-time six-digit code (all numbers) randomly.
def get_otp():
    # create a list of the digits we need
    digits = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    # total digits we need
    counter = 6
    # return string
    output = ""
    # 1. pick six digits at random from the list and return those.
    # 2. use random.random() to get a random number from 0 - 1
    # 3. multiply by 10 to get an integer from 0 - 10
    # 4. use math.floor() to get the integer (0 - 9)
    # 5. use str() to change that to a string.
    for digit in range(counter):
        index = math.floor(random.random() * 10)
        output += str(digits[index])

    return output

# save a OTP to the database.
# table = otp
#   id (key - auto)
#   userid -> integer, user id
#   otp -> varchar(6)
#   otp_time -> datetime
#   valid -> boolean (defaut is false, so need to set this manually)
def save_otp(user_id, otp, otp_time):
    db = sqlite3.connect(otp_db)
    db.row_factory = sqlite3.Row
    cur = db.cursor()
    # delete any existing OTP's for this user
    sql = 'update otp set valid = false where user_id = ?'
    cur.execute(sql, [user_id])
    db.commit()
    # insert this new OTP
    sql = 'insert into otp (user_id, otp, otp_time, valid) values (?, ?, ?, ?)'
    cur.execute(sql, [user_id, otp, otp_time, 1])
    db.commit()
    lastid = cur.lastrowid
    db.close()
    return lastid

# pass a user_id, otp and duration (in seconds) and check if:
#   1. OTP is valid (check valid flag)
#   2. time has not expired (i.e., now - otp_time < duration) (default = 5 minutes = 300 seconds)
def check_otp(user_id, otp, duration=300):
    # save current time for use later.
    now = datetime.now()
    db = sqlite3.connect(otp_db)
    db.row_factory = sqlite3.Row
    cur = db.cursor()
    sql = 'select id, user_id, otp, otp_time, valid from otp where user_id = ? and otp = ? and valid = true'
    cur.execute(sql, [user_id, otp])
    data = cur.fetchone()
    if data is None:
        return False
    else:
        # calculate the duration between otp_time (from db) and now (using datetime.now())
        otp_time = data['otp_time']
        # format is YYYY-MM-DD HH:MM:SS.sssss - so strip .sssss at end and convert to datetime object
        ms_pos = otp_time.rfind('.')
        otp_time = otp_time[:ms_pos]
        otp_time = datetime.strptime(otp_time, '%Y-%m-%d %H:%M:%S')
        # calculate the time difference between the time in the database (otp created)
        # and the time now (checking time)
        diff = now - otp_time
        # convert this to seconds
        diff = diff.total_seconds() / timedelta(minutes=1).total_seconds()
        # if diff is greater than the duration (default = 300 seconds) return False
        if diff > duration:
            return False
        
    # otp is valid
    return True

