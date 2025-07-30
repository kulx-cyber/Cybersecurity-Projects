import requests
import logging

# Setup logging
log_file = "scan_log.txt"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def perform_scan(target_url):
    if not target_url:
        print("Target URL is required.")
        return

    try:
        # Fetch target URL content
        response = requests.get(target_url)
        response_text = response.text
        response_headers = response.headers

        # Print response headers
        print("Response Headers:")
        for header, value in response_headers.items():
            print(f"{header}: {value}")

        # Initialize vulnerability checks
        vulnerabilities = []

        # 1. Cross-Site Scripting (XSS)
        if "<script>" in response_text:
            vulnerabilities.append("Possible XSS vulnerability detected.")

        # 2. Insecure Protocol (Cryptographic Failures)
        if "http://" in target_url:
            vulnerabilities.append("Insecure protocol detected. Use HTTPS with HSTS headers.")

        # 3. Missing Security Headers (Security Misconfiguration)
        if "X-Content-Type-Options" not in response_headers:
            vulnerabilities.append("Missing 'X-Content-Type-Options' header.")

        if "Strict-Transport-Security" not in response_headers:
            vulnerabilities.append("Missing 'Strict-Transport-Security' header.")

        # 4. SQL Injection Detection (Injection)
        if "error in your SQL syntax" in response_text.lower():
            vulnerabilities.append("Potential SQL injection detected.")

        # 5. Outdated Components (Vulnerable and Outdated Components)
        if "jquery-1." in response_text.lower():
            vulnerabilities.append("Outdated JavaScript library detected: Update jQuery to the latest version.")

        # 6. Sensitive Information Disclosure (Security Logging and Monitoring Failures)
        if "stack trace" in response_text.lower():
            vulnerabilities.append("Sensitive information leakage detected in error logs or debug output.")

        # 7. Server-Side Request Forgery (SSRF)
        if "url=" in target_url:
            vulnerabilities.append("Potential SSRF detected. Validate and sanitize external URL inputs.")

        # Log scan results
        scan_result = {
            "target_url": target_url,
            "vulnerabilities": vulnerabilities
        }
        logging.info(f"Scan completed for {target_url}. Vulnerabilities found: {vulnerabilities}")

        # Print results
        print("Scan completed.")
        if vulnerabilities:
            print("Vulnerabilities found:", vulnerabilities)
        else:
            print("No vulnerabilities detected.")

    except Exception as e:
        logging.error(f"Error scanning {target_url}: {str(e)}")
        print("Error:", str(e))

if __name__ == '__main__':
    target_url = input("Enter the target URL to scan: ")
    perform_scan(target_url)