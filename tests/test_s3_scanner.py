import sys
from pathlib import Path
from botocore.exceptions import ClientError


PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
	sys.path.insert(0, str(PROJECT_DIR))


class DummyLogger:
	def info(self, *args, **kwargs):
		pass
	def warning(self, *args, **kwargs):
		pass
	def error(self, *args, **kwargs):
		pass


def client_error(code, message="", operation="Operation"):
	return ClientError({"Error": {"Code": code, "Message": message}}, operation)


class S3Client:
	def list_buckets(self):
		return {"Buckets": [{"Name": "bucket1"}]}

	def get_public_access_block(self, Bucket):
		# No PAB configured
		raise client_error('NoSuchPublicAccessBlockConfiguration')

	def put_public_access_block(self, Bucket, PublicAccessBlockConfiguration):
		return {}

	def get_bucket_encryption(self, Bucket):
		raise client_error('ServerSideEncryptionConfigurationNotFoundError')

	def put_bucket_encryption(self, Bucket, ServerSideEncryptionConfiguration):
		return {}

	def get_bucket_versioning(self, Bucket):
		return {}

	def put_bucket_versioning(self, Bucket, VersioningConfiguration):
		return {}

	def get_bucket_logging(self, Bucket):
		return {}


class MockSession:
	def client(self, name):
		assert name == 's3'
		return S3Client()


def test_s3_scanner_check_runs():
	from scanner.aws import s3_scanner

	session = MockSession()
	logger = DummyLogger()
	# No log bucket in policy to keep logging remediation skipped
	s3_scanner.check(session=session, logger=logger, dry_run=True, policy={})

