#%%
import pycurl
# needed to predict total file size
import requests
# progress bar
from tqdm import tqdm
from io import BytesIO
import os


def upload_file(path, url):
    total_size = os.path.getsize(path)
    block_size = 1024

    # create a progress bar and update it manually
    with tqdm(total=total_size, unit='iB', unit_scale=True) as pbar:
        # store dotal dl's in an array (arrays work by reference)
        total_dl_d = [0]
        def status(download_t, download_d, upload_t, upload_d, total=total_dl_d):

            # increment the progress bar
            pbar.update(upload_d - total[0])
            # update the total dl'd amount
            total[0] = upload_d

        # download file using pycurl
        with open(path, 'rb') as f:
            c = pycurl.Curl()
            c.setopt(c.URL, url)
            c.setopt(c.POST, 1)
            c.setopt(c.HTTPPOST, [('title', 'test'), (('file', (c.FORM_FILE, path)))])
            # follow redirects:
            c.setopt(c.FOLLOWLOCATION, True)
            # custom progress bar
            c.setopt(c.NOPROGRESS, False)
            c.setopt(c.XFERINFOFUNCTION, status)

            bodyOutput = BytesIO()
            headersOutput = BytesIO()
            c.setopt(c.WRITEFUNCTION, bodyOutput.write)
            c.setopt(c.HEADERFUNCTION, headersOutput.write)
            c.perform()
            c.close()