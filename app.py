'''
    Send a onetime code (a.k.a. OTP) to the user via SMS and/or Email.
'''

from flask import Flask, render_template, request, session
from sendEmail import send_message
from database import get_db, onetime, otp_ontime
from datetime import datetime, timedelta
from sendEmail import send_otp_email
from sms import sendSMS
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)

# default form is a login form asking for the username/password.
# user access is in the table onetime -> users.
@app.route('/', methods=['GET', 'POST'])
def login():
    # display login screen
    if request.method == 'POST':
        # do post stuff, get the username and password
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        cur = db.cursor()
        sql = 'select id, username, password, email, phone, locked from users where username = ? and password = ?'
        cur.execute(sql, [username, password])
        data = cur.fetchone()
        # if we don't get back anything from the database (name/password combination is wrong)
        # or the 'locked' field is true.
        if data is None:
            return render_template('login.html', message='Invalid User or Password')
        elif data['locked']:
            return render_template('login.html', message='Your account is locked, see your boss')

        # create a user object to hold the data we just got back from the database
        user = {
            'id': data['id'],
            'username': data['username'],
            'email': data['email'],
            'phone': data['phone'],
            'locked': data['locked']
        }
        # add this user to the session variable
        session['user'] = user
        # get a otp from the function we've defined. This returns a string of six digits.
        otp = onetime()
        # print(f'otp = {otp}')
        # put this otp into the access table which we'll use to check.
        # first invalidate any existing tokens [excellent]
        sql = 'update access set valid = false where userid = ?'
        cur.execute(sql, [user['id']])
        db.commit()
        # get the current date/time and add 5 minutes for authentication.
        now = datetime.now()
        # insert the new otp into the database.
        sql = 'insert into access (userid, otp, otp_time, valid) values (?, ?, ?, ?)'
        cur.execute(sql, [user['id'], otp, now, True])
        db.commit()
        
        # send the otp to the user's email address
        message = f"Your OTP to login to the application is {otp}"
        send_otp_email(message, user['email'])
        # also send an SMS message to the user's telephone number
        sendSMS(message, user['phone'])
        
        return render_template('response.html', user=user)

    return render_template('login.html')

@app.route('/check_otp', methods=['GET', 'POST'])
def check_otp():
    # check the onetime secret obtained.
    message = "Request was not POST"
    if request.method == "POST":
        otp = request.form['otp']
        userid = session['user']['id']
        now = datetime.now()
        # two things to check. 1) if OTP is correct, 2) if within time limit
        db = get_db()
        cur = db.cursor()
        sql = 'select id, userid, otp, otp_time, valid from access where userid = ? and valid = true'
        cur.execute(sql, [userid])
        data = cur.fetchone()
        if data is None:
            message = 'Invalid OTP. Try Again'
        else:
            # check the actual value of the OTP
            if data['otp'] == otp:
                # check to see if the OTP was received within the time window
                if otp_ontime(data['otp_time'], now, 2):
                    message = f'OTP is OK, and time is OK!'
                    # at this time we can also update this user's OTP's in the access table
                    # to indicate that the one we sent is now used.
                    sql = 'update access set valid = false where userid = ? and otp = ? and valid = true'
                    cur.execute(sql, [userid, otp])
                    db.commit()
                else:
                    message = f"OTP is OK, but it's late"
                    # also set this OTP to be invalid for the user
                    sql = 'update access set valid = false where userid = ? and otp = ? and valid = true'
                    cur.execute(sql, [userid, otp])
                    db.commit()
            else:
                message = f"You Missed it! - try again"
            return render_template('otp_response.html', message=message)
    return render_template('response.html', message=message)

# test email
@app.route('/test')
def test():
    send_message()
    return "message sent"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='8080')
