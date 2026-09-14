import ssl
import requests
from urllib3.exceptions import InsecureRequestWarning

# Suppress insecure request warnings
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Bypass SSL verification globally for python
ssl._create_default_https_context = ssl._create_unverified_context
import os
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

# Patch requests.sessions.Session.request to default verify=False
original_request = requests.Session.request
def patched_request(self, method, url, **kwargs):
    kwargs['verify'] = False
    return original_request(self, method, url, **kwargs)
requests.Session.request = patched_request

import kaggle

print("Authenticating to Kaggle...")
kaggle.api.authenticate()

print("Downloading dataset (~3 GB)...")
kaggle.api.dataset_download_files('kmader/skin-cancer-mnist-ham10000', path='ham10000_raw', unzip=True, quiet=False)

print("Download and extraction complete!")
