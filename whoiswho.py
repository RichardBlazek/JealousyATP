import td
import json

if not td.authorize():
    sys.exit('Not authorized')

contacts = {user['id']: user['last_name'] + ' ' + user['first_name'] for user in td.get_users(td.get_contacts())}

with open('names.txt', mode = 'w') as out:
    print(json.dumps(contacts), file = out)

