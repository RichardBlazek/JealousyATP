from ctypes import *
import json
import sys

# load shared library
_td = CDLL('libtdjson.so')

# load TDLib functions from shared library
_create_client_id = _td.td_create_client_id
_create_client_id.restype = c_int
_create_client_id.argtypes = []

_receive = _td.td_receive
_receive.restype = c_char_p
_receive.argtypes = [c_double]

_send = _td.td_send
_send.restype = None
_send.argtypes = [c_int, c_char_p]

_execute = _td.td_execute
_execute.restype = c_char_p
_execute.argtypes = [c_char_p]

log_message_callback_type = CFUNCTYPE(None, c_int, c_char_p)

_set_log_message_callback = _td.td_set_log_message_callback
_set_log_message_callback.restype = None
_set_log_message_callback.argtypes = [c_int, log_message_callback_type]

# initialize TDLib log with desired parameters
@log_message_callback_type
def _log_message_callback(verbosity_level, message):
    if verbosity_level == 0:
        sys.exit('TDLib fatal error: %r' % message)

_set_log_message_callback(2, _log_message_callback)

def execute(type, **kwargs):
    result = _execute(json.dumps(kwargs | {'@type': type}).encode('utf-8'))
    if result:
        result = json.loads(result.decode('utf-8'))
    return result

def receive(time = 0.2):
    result = _receive(time)
    if result:
        result = json.loads(result.decode('utf-8'))
    return result

def wait_for(type):
    response = None
    while not response or response['@type'] != type:
        response = receive(10.0)
    return response

def wait_for_many(type, count):
    return [wait_for(type) for i in range(count)]

_client_id = _create_client_id()

def send(type, **kwargs):
    _send(_client_id, json.dumps(kwargs | {'@type': type}).encode('utf-8'))

def authorize():
    send('getAuthorizationState')
    while True:
        state = wait_for('updateAuthorizationState')['authorization_state']['@type']
        if state == 'authorizationStateReady':
            return True
        if state == 'authorizationStateClosed':
            return False

        # you MUST obtain your own api_id and api_hash at https://my.telegram.org
        if state == 'authorizationStateWaitTdlibParameters':
            send('setTdlibParameters', parameters = {'database_directory': 'ib', 'use_message_database': True, 'use_secret_chats': True,
                'api_id': 13925979, 'api_hash': '56f6469be7bcebe179004ec064aebe0c', 'system_language_code': 'en', 'device_model': 'Desktop',
                'application_version': '1.0', 'enable_storage_optimizer': True})

        # set an encryption key for database to let know TDLib how to open the database
        if state == 'authorizationStateWaitEncryptionKey':
            send('checkDatabaseEncryptionKey', encryption_key = '')

        # enter phone number to log in
        if state == 'authorizationStateWaitPhoneNumber':
            send('setAuthenticationPhoneNumber', phone_number = input('Please enter your phone number: '))

        # wait for authorization code
        if state == 'authorizationStateWaitCode':
            send('checkAuthenticationCode', code = input('Please enter the authentication code you received: '))

        # wait for first and last name for new users
        if state == 'authorizationStateWaitRegistration':
            send('registerUser', first_name = input('Please enter your first name: '), last_name = input('Please enter your last name: '))

        # wait for password if present
        if state == 'authorizationStateWaitPassword':
            send('checkAuthenticationPassword', password = input('Please enter your password: '))


def get_contacts():
    send('getContacts')
    return wait_for('users')['user_ids']

def get_users(ids):
    for id in ids:
        send('getUser', user_id = id)
    return wait_for_many('user', len(ids))

# setting TDLib log verbosity level to 1 (errors)
execute('setLogVerbosityLevel', new_verbosity_level = 1)

