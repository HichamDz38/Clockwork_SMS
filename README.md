# Clockwork_SMS
tools that facilitate the work with the Clockwork SMS API
this tools is designer to send multiples SMS by using multiple accounts

# prerequisite
clockwork: pip install clockwork

# Files structure
accounts.txt : list of accounts(API key), each key in a single line
jobs.txt : list of the SMS to send in the format [name]:[phone number]
senders.txt: list of the phone number, each phone number in a single line (by using this API you can modify the sender number so the reciever can get a message from someone else)
body.txt: the body of the SMS, it's dynamique messages (_To: mean the name of the reciever, _From: mean the name of the sender)

# how to use
python clockwork_sms.py
