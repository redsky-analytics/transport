from transport.transport import get
import sys, shutil
import fire, getpass
import confuse
from pathlib import Path
import requests
import json


app_name = 'untangler-cli'

if not Path(f'~/.config/{app_name}/config.yaml').expanduser().exists():
    Path(f'~/.config/{app_name}/').expanduser().mkdir(parents=True, exist_ok=True)
    source = Path(__file__).parent.parent / 'cli.yml'
    shutil.copy(str(source), str(Path(f'~/.config/{app_name}/config.yaml').expanduser()))
    

config = confuse.Configuration(app_name)

def print_json(d):
    print(json.dumps(d, indent=2))

def update_config(d):

    for k in d:
        config[k] = d[k]

    config_filename = Path(config.config_dir()) / confuse.CONFIG_FILENAME
    config_filename.write_text(config.dump())
    
def auth(email, password):
    webKey = config['FB'].get()
    url = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={webKey}'
    response = requests.post(url, json={        
        "email": email,
        "password": password,
        "returnSecureToken": True 
        })
    return response.json()

def refresh_auth_token():
    webKey = config['FB'].get()
    refreshToken = config['refreshToken'].get()
    
    url = f'https://securetoken.googleapis.com/v1/token?key={webKey}'
    response =  requests.post(
        url,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data=f'grant_type=refresh_token&refresh_token={refreshToken}'
    )
    result = response.json()
    idToken = result['access_token']
    refreshToken = result['refresh_token']
    update_config({'idToken': idToken, 'refreshToken': refreshToken })

def retry(original_function):
    def wrapper(*args, **kwargs):
        result = original_function(*args, **kwargs)

        if 'message' in result and result['message'] == 'Unauthorized':
            refresh_response = refresh_auth_token()
            result = original_function(*args, **kwargs)
        return result
    return wrapper

@retry
def http_get(*path_parts):
    base_url = config['HTTP'].get()
    token = config['idToken'].get()
    url = '/'.join([base_url] + list(path_parts))
    response = requests.get(url, headers={'Authorization': token})
    return response.json()

@retry
def http_delete(*path_parts, data=None):
    base_url = config['HTTP'].get()
    token = config['idToken'].get()
    url = '/'.join([base_url] + list(path_parts))
    
    content = {} if data is None else {'Content-Type': 'application/json'}
    headers = {'Authorization': token, **content}

    if data is None:
        response = requests.delete(url, headers=headers)
    else:
        response = requests.delete(url, headers=headers, data=json.dumps(data))
    
    return response.json()

@retry
def http_post(*path_parts, data=None):
    base_url = config['HTTP'].get()
    token = config['idToken'].get()
    url = '/'.join([base_url] + list(path_parts))

    content = {} if data is None else {'Content-Type': 'application/json'}
    headers = {'Authorization': token, **content}

    if data is None:
        response = requests.post(url, headers=headers)
    else:
        response = requests.post(url, headers=headers, data=json.dumps(data))
    
    return response.json()

@retry
def http_put(*path_parts, data=None):
    base_url = config['HTTP'].get()
    token = config['idToken'].get()
    url = '/'.join([base_url] + list(path_parts))
    content = {} if data is None else {'Content-Type': 'application/json'}
    headers = {'Authorization': token, **content}

    if data is None:
        response = requests.post(url, headers=headers)
    else:
        response = requests.put(url, headers={'Authorization': token, **content}, data=json.dumps(data))
    return response.json()


class UntanglerCli(object):
    """A cli to handle untangler data and models."""

    def login(self, username=None):
        '''Login is valid for 1 hour'''
        if username is None:
            username = config['email'].get()
            if not username:
                raise Exception('Username is not specified')
        else:
            update_config({'email': username})
        
        password = getpass.getpass(f'Password for {username}: ')
        r = auth(username, password)
        if 'error' in r:
            error = r['error']
            raise Exception(f"error {error['code']}: {error['message']}")

        idToken = r['idToken']
        refreshToken = r['refreshToken']
        update_config({'idToken': idToken, 'refreshToken': refreshToken })

    def logout(self):
        update_config({'idToken': None, 'refreshToken': None })

    def collections(self):
        '''Get the list of collections'''
        print_json(http_get('collections'))

    def collection(self, id, function=None, data=None, itemFunction=None, itemData=None):
        
        '''Manipulate a single collection'''
        if function is not None and  function not in ['create', 'delete', 'update', 'copyto', 'rename', 'shares', 'share', 'unshare', 'download', 'upload', 'items', 'item']:
            raise Exception(f'Bad function {function}')

        if function is None:
            return  print_json(http_get('collection', id))
        elif function == 'create':
            return print_json(http_post('collection', id, data=data))
        elif function == 'delete':
            return print_json(http_delete('collection', id))
        elif function == 'update':
            if data is not None:
                return print_json(http_put('collection', id, data=data))
            return 'Nothing to update'
        elif function == 'copyto':
            if data is not None:
                return print_json(http_post('collection', id, 'copyto', data))
            return 'Target name is not specified'
        elif function == 'rename':
            if data is not None:
                result = http_post('collection', id, 'copyto', data)
                http_delete('collection', id)
                return print_json(result)
            return 'Target name is not specified'

        elif function == 'shares':
            return print_json(http_get('collection', id, 'shares'))
        elif function == 'share':
            emails = [x.strip() for x in data.split(',')]
            is_valid = all(['@' in x for x in emails])
            if is_valid:
                return print_json(http_post('collection', id, 'shares', data={"Emails": emails}))
            else:
                raise Exception('Email list is not valid. Provide a comma separated list of emails. No spaces.')
        elif function == 'unshare':
            emails = [x.strip() for x in data.split(',')]
            is_valid = all(['@' in x for x in emails])
            if is_valid:
                return print_json(http_delete('collection', id, 'shares', data={"Emails": emails}))
            else:
                raise Exception('Email list is not valid. Provide a comma separated list of emails. No spaces.')
        elif function == 'upload':
            return http_get('collection', id, 'upload')
        elif function == 'download':
            return http_get('collection', id, 'download')
        elif function == 'items':
            return print_json(http_get('collection', id, 'items'))
        elif function == 'item':
            itemName = data
            if itemName is None:
                raise Exception('Item name is required')

            if itemFunction is not None and itemFunction not in ['add', 'delete', 'update', 'download', 'upload']:
                raise Exception(f'Item function "{itemFunction}" is not recognized.')

            if itemFunction is None:
                return print_json(http_get('collection', id, 'item', itemName))

            if itemFunction == 'add':
                if itemData is None:
                    return print_json(http_post('collection', id, 'items', data={'Item': itemName}))
                return print_json(http_post('collection', id, 'items', data={**itemData, 'Item': itemName}))

            if itemFunction == 'delete':
                return print_json(http_delete('collection', id, 'item', itemName))

            if itemFunction == 'update':
                if itemData is None:
                    print("Nothing to update")
                    return
                    
                return print_json(http_put('collection', id, 'item', itemName, data=itemData))

        print('Unimplemented')

    def progress(self, id, data=None, wait=None):
        '''Check progress / wait for completion'''
        print('cc')

def run():
    ucli = UntanglerCli()
    # ucli.login()
    fire.Fire(ucli)

if __name__ == '__main__':
  run()


# def cliget():
#     token = sys.argv[1]
#     get(token)
    
# if __name__ == '__main__':
#     cliget()