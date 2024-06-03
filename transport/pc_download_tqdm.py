#%%
import pycurl
# needed to predict total file size
import requests
# progress bar
from tqdm import tqdm


def download_file(url, path):
    # show progress % and amount in bytes
    r = requests.head(url)
    print(r.headers)
    total_size = int(r.headers.get('content-length', 0))
    block_size = 1024
    print('total_size', total_size)
    # create a progress bar and update it manually
    with tqdm(total=total_size, unit='iB', unit_scale=True) as pbar:
        # store dotal dl's in an array (arrays work by reference)
        total_dl_d = [0]
        def status(download_t, download_d, upload_t, upload_d, total=total_dl_d):
            # increment the progress bar
            pbar.update(download_d - total[0])
            # update the total dl'd amount
            total[0] = download_d

        # download file using pycurl
        with open(path, 'wb') as f:
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(pycurl.SSL_VERIFYPEER, 0)   
            c.setopt(pycurl.SSL_VERIFYHOST, 0)
            c.setopt(c.WRITEDATA, f)
            # follow redirects:
            c.setopt(c.FOLLOWLOCATION, True)
            # custom progress bar
            c.setopt(c.NOPROGRESS, False)
            c.setopt(c.XFERINFOFUNCTION, status)
            c.perform()
            c.close()