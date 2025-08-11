## Cloud Misconfiguration Scanner (AWS)

Cloud Misconfiguration Scanner scans your AWS environment for common security misconfigurations and can optionally remediate them. It’s driven by a YAML policy file and supports dry-run mode for safe evaluation.

### Features
- Service coverage: S3, IAM, EC2, RDS, CloudTrail, CloudWatch, ELB, EBS, Lambda, SSM, SNS, SQS
- Inline remediation inside each scanner, guarded by dry-run
- YAML-based policy with per-service toggles and parameters
- Interactive service selection
- Structured logging (console + rotating file)

### Requirements
- Python 3.9+
- AWS credentials configured (env vars, shared credentials file, or interactive)
- Dependencies from `requirements.txt`

### Install
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configure
Edit `config/policy.yaml`. Key sections:
- global
	- dry_run: true to prevent any changes
	- region: default AWS region
	- log_level: DEBUG/INFO/WARNING/ERROR
	- scan_all: true scans all enabled services by default
- services
	- Each service has `enabled` and `checks` arrays, plus optional knobs the scanners use for remediation.

Important optional keys (add your values as needed):
- services.s3.s3_log_bucket: target bucket for access logs when enabling S3 logging
- services.ec2.kms_key_id: KMS Key ID/ARN to encrypt EBS volumes (modify_volume)
- services.rds.backup_retention_days: minimum backup retention days
- services.lambda.kms_key_arn: KMS key for environment variables encryption
- services.lambda.tracing_enabled: enable X-Ray tracing
- services.sns.kms_key_arn: KMS key for SNS at-rest encryption (defaults to alias/aws/sns if empty)

#### Policy keys reference
global:
- dry_run (bool): master switch for read-only mode; CLI --dry-run also sets this
- region (string): default AWS region (e.g., us-east-1)
- log_level (string): DEBUG, INFO, WARNING, ERROR, CRITICAL
- scan_all (bool): when true, show all services marked enabled

services:
- s3:
	- enabled (bool), checks (list)
	- s3_log_bucket (string): bucket to receive access logs; if empty, logging remediation is skipped
- ec2:
	- enabled (bool), checks (list)
	- kms_key_id (string): KMS key ID/ARN used for encrypting unencrypted EBS volumes
- rds:
	- enabled (bool), checks (list)
	- backup_retention_days (int): enforce if current retention is lower (default 7)
- lambda:
	- enabled (bool), checks (list)
	- kms_key_arn (string): KMS key ARN to encrypt environment variables; if empty, skip remediation
	- tracing_enabled (bool): enable X-Ray tracing when false currently
- sns:
	- enabled (bool), checks (list)
	- kms_key_arn (string): KMS key ARN; if empty, code defaults to alias/aws/sns under your account/region
- sqs, ssm, cloudtrail, cloudwatch, elb, ebs, iam:
	- enabled (bool), checks (list)

Notes:
- Some remediations require privileges (e.g., IAM detach policy, EC2 modify volume); ensure the executing role has needed permissions.
- For S3 access logs, the target bucket must exist and allow writes from the source bucket’s region.

### Run
```bash
python main.py --policy ./config/policy.yaml --dry-run
```
- The CLI will prompt you to select which services to scan.
- With `--dry-run`, only scan and remediation plans are logged; no API changes are made.
- Omit `--dry-run` to allow remediation. The app will pause and prompt before making changes.

Common options:
- --interactive: ask for AWS credentials interactively
- --cloud aws: currently AWS is supported
- --log-level INFO: set console/file logging verbosity
- --log ./logs/cloud_scanner.log: custom log file path

### Service behaviors (high level)
- S3: enforce PublicAccessBlock, enable default encryption (AES256), versioning, and optionally access logs to s3_log_bucket.
- IAM: remove overly permissive inline/attached policies, tighten password policy, MFA check (interactive).
- EC2: revoke 0.0.0.0/0 ingress, require IMDSv2, remove public IPs, encrypt unencrypted volumes (using kms_key_id).
- RDS: disable public access, set backup retention, enable deletion protection, log advisory for storage encryption (snapshot/restore required).
- CloudTrail: ensure logging/multi-region/log-file validation.
- CloudWatch: ensure basic security alarms exist.
- ELB: enable deletion protection, set idle timeout, update SSL policy, enable access logs.
- EBS: delete unattached volumes; remove public snapshot access; encryption advisory for existing volumes.
- Lambda: set timeout max 60s, enable tracing, detach overly permissive policies, encrypt env vars with kms_key_arn if provided.
- SSM: remove public doc sharing, configure Session Manager logging, set up patch compliance (safe defaults).
- SNS: remove public policies, enable encryption with kms_key_arn or alias/aws/sns, skip unsubscribing pending subs.
- SQS: enable SSE with alias/aws/sqs, remove public policies, configure DLQ if missing.

### Safety notes
- Always start with `--dry-run` and review logs.
- Some settings (e.g., RDS storage encryption) cannot be changed in-place; remediation logs guidance.
- IAM and networking changes can be disruptive; ensure proper approvals.

### Troubleshooting
### Testing
Unit tests use lightweight local mocks per service; no AWS credentials are required.

- Install and run all tests:
	```bash
	pip install -r requirements.txt
	pytest -q
	```

- Run a single scanner test:
	```bash
	pytest -q tests/test_s3_scanner.py
	pytest -q tests/test_ec2_scanner.py
	# ... similarly for each test_*.py in tests/
	```

- Run the consolidated smoke test that exercises all scanners:
	```bash
	pytest -q tests/test_all_scanners.py
	```

Notes:
- Tests mock AWS clients in-process, so nothing is created/modified in AWS.
- If you add a new scanner, copy any existing test_*.py file as a template, stub the minimal client methods that your scanner uses, and call check(session=MockSession(), logger=DummyLogger(), dry_run=True, policy={}).

Optional manual smoke (no changes):
```bash
python main.py --policy ./config/policy.yaml --dry-run
```
Select a couple of services when prompted to validate end-to-end flow.

- Missing boto3/botocore/PyYAML errors: install dependencies with `pip install -r requirements.txt`.
- Permission errors: ensure your AWS credentials have necessary permissions for describe and modify APIs.
- Logging: check `./logs/cloud_scanner.log` for details.

### Test result reports (JUnit XML)
To record results for the consolidated run and individual tests, you can:

- Use pytest flags directly:
	```bash
	pytest -q tests/test_all_scanners.py --junitxml=reports/test_all_scanners.xml
	pytest -q tests/test_s3_scanner.py --junitxml=reports/test_s3_scanner.xml
	```

- Or run the helper script that generates reports for the smoke test, each per-scanner test, and the full suite:
	```bash
	scripts/run_tests_with_reports.sh
	```

Reports will be written under `reports/`:
- reports/test_all_scanners.xml
- reports/test_<service>_scanner.xml
- reports/combined.xml

These XML files can be uploaded to CI systems (e.g., GitHub Actions) for test reporting and trends.

### Contributing
1. Create a branch
2. Make changes and add tests
3. Submit a PR

### License
This is open source software.
