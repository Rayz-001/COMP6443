import re
import time
import urllib.parse
import requests

HAAS_URL = "https://haas-v4.quoccacorp.com/"
TARGET_HOST = "kb.quoccacorp.com"

# --- Helpers to build raw HTTP requests inside HAAS ---
def build_get(path: str, cookie: str | None = None) -> str:
    lines = [
        f"GET {path} HTTP/1.1",
        f"Host: {TARGET_HOST}",
        "Accept: text/html,*/*",
        "Connection: close",
    ]
    if cookie:
        lines.insert(2, f"Cookie: {cookie}")
    return "\r\n".join(lines) + "\r\n\r\n"

def build_post_form(path: str, form: dict, cookie: str | None = None) -> str:
    body = urllib.parse.urlencode(form)
    lines = [
        f"POST {path} HTTP/1.1",
        f"Host: {TARGET_HOST}",
        "Accept: text/html,*/*",
        "Content-Type: application/x-www-form-urlencoded",
        f"Content-Length: {len(body.encode('utf-8'))}",
        "Connection: close",
    ]
    if cookie:
        # put Cookie header before body
        lines.insert(2, f"Cookie: {cookie}")
    return "\r\n".join(lines) + "\r\n\r\n" + body

# --- Parse the upstream (kb) response that HAAS returns as text/plain ---
def split_upstream(raw_text: str) -> tuple[str, str]:
    """
    HAAS returns the upstream response as plain text like:
      HTTP/1.1 200 OK
      Header: ...
      ...
      
      <html>...</html>
    """
    # Normalise newlines
    txt = raw_text.replace("\r\n", "\n")
    parts = txt.split("\n\n", 1)
    if len(parts) == 1:
        return txt, ""
    return parts[0], parts[1]

def extract_cookie(upstream_headers: str) -> str | None:
    """
    Extract first Set-Cookie (if present) and return a Cookie header value like:
      session=...
    """
    # Look for Set-Cookie: session=...;
    m = re.search(r"^Set-Cookie:\s*([^;\n]+)", upstream_headers, flags=re.MULTILINE | re.IGNORECASE)
    if not m:
        return None
    return m.group(1).strip()

def extract_question(html: str) -> tuple[int, str, int] | None:
    """
    Finds: What is 74+54? (also supports -, *, / just in case)
    """
    m = re.search(r"What is\s+(\d+)\s*([+\-*/])\s*(\d+)\s*\?", html)
    if not m:
        return None
    a = int(m.group(1))
    op = m.group(2)
    b = int(m.group(3))
    return a, op, b

def solve(a: int, op: str, b: int) -> int:
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/":
        # If division appears, it’s usually exact integer in these challenges
        return a // b
    raise ValueError(f"Unknown operator: {op}")

def haas_send(session: requests.Session, raw_request: str) -> str:
    # HAAS expects form field requestBox with your raw HTTP request
    r = session.post(HAAS_URL, data={"requestBox": raw_request}, timeout=10)
    r.raise_for_status()
    return r.text

def main():
    s = requests.Session()
    # Skip trying to verify TLS certs, due to Burp's CA.
    s.verify = False
    # Proxy requests through Burp.
    s.proxies = {"https": "http://127.0.0.1:8080"}
    cookie = None

    start = time.time()

    # 1) Get first question from kb via HAAS
    raw = haas_send(s, build_get("/"))
    hdrs, body = split_upstream(raw)
    cookie = extract_cookie(hdrs) or cookie

    # 2) Loop answering until we see a flag / success
    for i in range(1, 40):  # safety cap
        # Check for flag-looking text anywhere
        if "flag" in body.lower() or "ctf" in body.lower():
            print("=== POSSIBLE FLAG PAGE ===")
            print(body)
            return

        q = extract_question(body)
        if not q:
            print("No question found. Full body below:")
            print(body)
            return

        a, op, b = q
        ans = solve(a, op, b)

        # Optional: keep an eye on the timer
        elapsed = time.time() - start
        print(f"[{i:02d}] {a}{op}{b} = {ans}  (elapsed {elapsed:.2f}s)")

        # Submit answer to kb via HAAS
        raw = haas_send(s, build_post_form("/", {"answer": str(ans)}, cookie=cookie))
        hdrs, body = split_upstream(raw)
        cookie = extract_cookie(hdrs) or cookie

        # If you want to be extra safe on timing, don’t sleep at all.
        # time.sleep(0.01)

    print("Reached loop cap without finding flag. Last page:")
    print(body)

if __name__ == "__main__":
    main()