#%%
from get_upload_url import geturl, puturl
from pc_download_tqdm import download_file
from pc_upload_tqdm import upload_file
from pathlib import Path

def get(token, fullpath=False):
    Path('localdata').mkdir(parents=True, exist_ok=True)
    
    path = Path('localdata') / Path(token).name
    url = geturl(token)
    download_file(url, path)

get('data/ms')