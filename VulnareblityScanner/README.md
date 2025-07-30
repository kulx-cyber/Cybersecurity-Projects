# Web Vulnerability Scanner

## Overview

This project implements a web vulnerability scanner that performs automated security assessments of web applications and websites. The scanner identifies common web vulnerabilities based on the OWASP Top 10 security risks and provides detailed reports with recommendations for remediation.

## Features

- **Automated Vulnerability Detection**: Scans web applications for common security vulnerabilities
- **OWASP Top 10 Coverage**: Detects major security risks including XSS, SQL Injection, and more
- **Security Headers Analysis**: Checks for missing or misconfigured security headers
- **Logging and Reporting**: Comprehensive scan results with timestamps and detailed findings
- **User-Friendly Interface**: Simple command-line interface for easy operation
- **Error Handling**: Robust error handling with detailed error logging

## Vulnerability Detection Capabilities

### 1. Cross-Site Scripting (XSS)
- Detects potential XSS vulnerabilities in web page content
- Identifies unsafe script tags and executable content

### 2. Cryptographic Failures
- Identifies insecure HTTP protocol usage
- Recommends HTTPS implementation with proper security headers

### 3. Security Misconfiguration
- **Missing Security Headers Detection**:
  - `X-Content-Type-Options` header
  - `Strict-Transport-Security` (HSTS) header
- Provides recommendations for proper security header implementation

### 4. Injection Attacks
- **SQL Injection Detection**: Identifies potential SQL injection vulnerabilities
- Analyzes error messages that might reveal database structure

### 5. Vulnerable and Outdated Components
- Detects outdated JavaScript libraries (e.g., jQuery 1.x)
- Recommends updating to latest secure versions

### 6. Security Logging and Monitoring Failures
- Identifies sensitive information disclosure
- Detects stack traces and debug information leakage

### 7. Server-Side Request Forgery (SSRF)
- Detects potential SSRF vulnerabilities in URL parameters
- Provides input validation recommendations

## Project Structure

```
VulnareblityScanner/
├── vulnerablityPrediction.py    # Main scanner implementation
├── scan_log.txt                 # Scan results and logs
└── README.md                   # Project documentation
```

## Requirements

Install the required dependencies:

```bash
pip install requests
```

### Dependencies
- **requests**: HTTP library for making web requests and analyzing responses

## Installation

1. **Clone or download the project**:
   ```bash
   git clone <repository-url>
   cd VulnareblityScanner
   ```

2. **Install dependencies**:
   ```bash
   pip install requests
   ```

3. **Run the scanner**:
   ```bash
   python vulnerablityPrediction.py
   ```

## Usage

### Basic Scan

1. **Start the scanner**:
   ```bash
   python vulnerablityPrediction.py
   ```

2. **Enter target URL**:
   ```
   Enter the target URL to scan: https://example.com
   ```

3. **View results**:
   - Immediate console output with detected vulnerabilities
   - Detailed logs saved to `scan_log.txt`

### Example Output

```
Response Headers:
Content-Type: text/html; charset=utf-8
Server: nginx/1.18.0
Date: Thu, 26 Dec 2024 20:48:34 GMT

Scan completed.
Vulnerabilities found: [
    "Missing 'X-Content-Type-Options' header.",
    "Missing 'Strict-Transport-Security' header."
]
```

## Log File Format

The scanner maintains detailed logs in `scan_log.txt`:

```
2024-12-26 20:48:34 - Scan completed for https://example.com. 
Vulnerabilities found: ["Missing 'X-Content-Type-Options' header."]

2024-12-26 20:50:13 - Error scanning https://invalid-url.com: 
HTTPSConnectionPool error details...
```

## Security Recommendations

### For Missing Security Headers:
- **X-Content-Type-Options**: Add `X-Content-Type-Options: nosniff`
- **HSTS**: Implement `Strict-Transport-Security: max-age=31536000; includeSubDomains`

### For Protocol Issues:
- Migrate from HTTP to HTTPS
- Implement proper SSL/TLS configuration
- Use security headers to enforce secure connections

### For Vulnerable Components:
- Regularly update JavaScript libraries and frameworks
- Implement dependency scanning in CI/CD pipelines
- Monitor for security advisories

## Limitations

- **Detection Method**: Uses pattern matching and header analysis
- **False Positives**: May generate false positives for complex applications
- **Scope**: Limited to basic vulnerability detection patterns
- **Authentication**: Does not handle authenticated scans
- **Advanced Attacks**: Does not detect complex attack vectors

## Future Enhancements

- **Advanced XSS Detection**: Implement payload injection testing
- **Authentication Support**: Add support for authenticated scans
- **Database Integration**: Store scan results in database
- **Report Generation**: Generate HTML/PDF reports
- **Multi-threading**: Implement concurrent scanning for multiple URLs
- **Custom Payloads**: Support for custom vulnerability detection patterns
- **API Integration**: REST API for automated security testing
- **Plugin System**: Extensible architecture for custom vulnerability checks

## Best Practices

1. **Permission**: Only scan websites you own or have permission to test
2. **Rate Limiting**: Implement delays between requests to avoid overwhelming targets
3. **Legal Compliance**: Ensure compliance with local laws and regulations
4. **Responsible Disclosure**: Report vulnerabilities responsibly to website owners

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-vulnerability-check`)
3. Commit your changes (`git commit -am 'Add new vulnerability detection'`)
4. Push to the branch (`git push origin feature/new-vulnerability-check`)
5. Create a Pull Request

## License

This project is open-source and available under the MIT License.

## Disclaimer

This tool is designed for educational and authorized security testing purposes only. Users are responsible for ensuring they have proper authorization before scanning any websites or web applications. The authors are not responsible for any misuse of this tool.

## Authors

- **Kulkarni** - Initial implementation

## Acknowledgments

- OWASP Top 10 Project
- Web security research community
- Python requests library developers