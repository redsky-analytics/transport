from transport.transport import get
import sys, shutil
import fire, getpass
import confuse
from pathlib import Path
import requests



app_name = 'untangler-cli'

if not Path(f'~/.config/{app_name}/config.yaml').expanduser().exists():
    Path(f'~/.config/{app_name}/').expanduser().mkdir(parents=True, exist_ok=True)
    source = Path(__file__).parent.parent / 'cli.yml'
    shutil.copy(str(source), str(Path(f'~/.config/{app_name}/config.yaml').expanduser()))
    

config = confuse.Configuration(app_name)


def http_get(path):
    base_url = config['HTTP'].get()
    token = config['idToken'].get()
    url = '/'.join([base_url, path])
    print(url)
    response = requests.get(url, headers={'Authorization': token})
    return response.json()

def auth(email, password):
    webKey = config['FB'].get()
    url = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={webKey}'
    response = requests.post(url, json={        
        "email": email,
        "password": password,
        "returnSecureToken": True 
        })
    return response.json()

def update_config(d):

    for k in d:
        config[k] = d[k]

    config_filename = Path(config.config_dir()) / confuse.CONFIG_FILENAME
    config_filename.write_text(config.dump())



class UntanglerCli(object):
    """A cli to handle untangler data and models."""

    def login(self, username=None):
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
        print(http_get('collections'))

    def collection(self, id, function=None, data=None):
        '''Manipulate a single collection'''
        if function is not None and  function not in ['del', 'update', 'items', 'share', 'unshare', 'download', 'upload']:
            raise Exception(f'Bad function {function}')

        print('aa')

    def item(self, id, function=None):
        '''Manipulate a single collection'''
        if function is not None and  function not in ['del', 'update', 'download']:
            raise Exception(f'Bad function {function}')
        print('bb')

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