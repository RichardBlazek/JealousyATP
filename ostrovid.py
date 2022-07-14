from time import time, sleep
import td
import json

def is_trackable(user):
    return user['status']['@type'] in {'userStatusOffline', 'userStatusOnline'}

def was_online(user, last_time):
    return user['status']['@type'] == 'userStatusOnline' or user['status']['was_online'] > last_time

def get_online(ids, last_time):
    return [user['id'] for user in td.get_users(ids) if is_trackable(user) and was_online(user, last_time)]

if not td.authorize():
    sys.exit('Not authorized')

contacts = td.get_contacts()
last_time = time()

while True:
    print(last_time, time())
    with open('onlines.txt', mode='a') as out:
        print(json.dumps(get_online(contacts, last_time)), file = out)
    last_time = time()
    sleep(60)
