#%%
import pycurl
# for displaying the output text
from sys import stderr as STREAM

# replace with your own url and path variables
url = "http://speedtest.tele2.net/100MB.zip"
path = 'test_file.dat'

# use kiB's
kb = 1024

# callback function for c.XFERINFOFUNCTION
def status(download_t, download_d, upload_t, upload_d):
    STREAM.write('Downloading: {}/{} kiB ({}%)\r'.format(
        str(int(download_d/kb)),
        str(int(download_t/kb)),
        str(int(download_d/download_t*100) if download_t > 0 else 0)
    ))
    STREAM.flush()

# download file using pycurl
with open(path, 'wb') as f:
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, f)
    # display progress
    c.setopt(c.NOPROGRESS, False)
    c.setopt(c.XFERINFOFUNCTION, status)
    c.perform()
    c.close()

# keeps progress on screen after download completes
print()