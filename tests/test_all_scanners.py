import sys
from pathlib import Path
from datetime import datetime, timezone

from botocore.exceptions import ClientError


# Ensure project root (cloud-misconfig-scanner) is on sys.path
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


def client_error(code: str, message: str = "Error", operation: str = "Operation"):
    return ClientError({"Error": {"Code": code, "Message": message}}, operation)


class MockSession:
    region_name = "us-east-1"

    def client(self, service_name: str):
        mapping = {
            "s3": S3Client,
            "ec2": EC2Client,
            "cloudtrail": CloudTrailClient,
            "cloudwatch": CloudWatchClient,
            "elbv2": ELBv2Client,
            "iam": IAMClient,
            "lambda": LambdaClient,
            "ssm": SSMClient,
            "sns": SNSClient,
            "sqs": SQSClient,
            "sts": STSClient,
            "kms": KMSClient,
            "logs": LogsClient,
            "rds": RDSClient,
        }
        cls = mapping.get(service_name)
        if not cls:
            raise AssertionError(f"Unexpected client requested: {service_name}")
        return cls()


class S3Client:
    def list_buckets(self):
        return {"Buckets": [{"Name": "bucket1"}]}

    def get_public_access_block(self, Bucket):
        return {"PublicAccessBlockConfiguration": {
            "BlockPublicAcls": False,
            "IgnorePublicAcls": False,
            "BlockPublicPolicy": False,
            "RestrictPublicBuckets": False,
        }}

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

    def head_bucket(self, Bucket):
        return {}

    def put_bucket_logging(self, Bucket, BucketLoggingStatus):
        return {}


class EC2Client:
    def describe_security_groups(self):
        return {
            "SecurityGroups": [
                {
                    "GroupId": "sg-1",
                    "IpPermissions": [
                        {
                            "FromPort": 22,
                            "ToPort": 22,
                            "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                        }
                    ],
                }
            ]
        }

    def revoke_security_group_ingress(self, GroupId, IpPermissions):
        return {}

    def describe_instances(self):
        return {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-1",
                            "MetadataOptions": {"HttpTokens": "optional"},
                            "PublicIpAddress": "1.2.3.4",
                        }
                    ]
                }
            ]
        }

    def modify_instance_metadata_options(self, InstanceId, HttpTokens):
        return {}

    def modify_instance_attribute(self, InstanceId, NoPublicIp):
        return {}

    def describe_volumes(self):
        return {"Volumes": [{"VolumeId": "vol-1", "Encrypted": False}]}

    def modify_volume(self, VolumeId, KmsKeyId=None):
        return {}

    # EBS related operations
    def delete_volume(self, VolumeId):
        return {}

    def describe_snapshots(self, OwnerIds=None):
        return {"Snapshots": [{"SnapshotId": "snap-1"}]}

    def describe_snapshot_attribute(self, SnapshotId, Attribute):
        return {"CreateVolumePermissions": [{"Group": "all"}]}

    def modify_snapshot_attribute(self, SnapshotId, Attribute, OperationType, GroupNames):
        return {}


class CloudTrailClient:
    def describe_trails(self):
        return {"trailList": [{"Name": "trail1", "IsMultiRegionTrail": False, "LogFileValidationEnabled": False}]}

    def get_trail_status(self, Name):
        return {"IsLogging": False}

    def start_logging(self, Name):
        return {}

    def update_trail(self, Name, **kwargs):
        return {}


class CloudWatchClient:
    def describe_alarms(self):
        return {"MetricAlarms": []}

    def put_metric_alarm(self, **kwargs):
        return {}


class ELBv2Client:
    def describe_load_balancers(self):
        return {"LoadBalancers": [{"LoadBalancerArn": "arn:lb", "LoadBalancerName": "lb1"}]}

    def describe_load_balancer_attributes(self, LoadBalancerArn):
        return {"Attributes": [
            {"Key": "deletion_protection.enabled", "Value": "false"},
            {"Key": "idle_timeout.timeout_seconds", "Value": "30"},
            {"Key": "access_logs.s3.enabled", "Value": "false"},
        ]}

    def modify_load_balancer_attributes(self, LoadBalancerArn, Attributes):
        return {}

    def describe_listeners(self, LoadBalancerArn):
        return {"Listeners": [{"Protocol": "HTTPS", "ListenerArn": "arn:listener", "SslPolicy": "OldPolicy"}]}

    def modify_listener(self, ListenerArn, SslPolicy):
        return {}


class IAMClient:
    def list_users(self):
        return {"Users": [{"UserName": "alice"}]}

    def list_user_policies(self, UserName):
        return {"PolicyNames": ["Inline1"]}

    def delete_user_policy(self, UserName, PolicyName):
        return {}

    def list_attached_user_policies(self, UserName):
        return {"AttachedPolicies": [{"PolicyArn": "arn:policy", "PolicyName": "Permissive"}]}

    def get_policy(self, PolicyArn):
        return {"Policy": {"DefaultVersionId": "v1"}}

    def get_policy_version(self, PolicyArn, VersionId):
        return {"PolicyVersion": {"Document": {"Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*"}]}}}

    def get_account_password_policy(self):
        return {"PasswordPolicy": {
            "RequiredSymbols": False,
            "MinimumPasswordLength": 6,
            "RequireUppercaseCharacters": False,
            "RequireLowercaseCharacters": True,
            "RequireNumbers": True,
        }}

    def update_account_password_policy(self, **kwargs):
        return {}

    def list_mfa_devices(self, UserName):
        return {"MFADevices": []}

    def create_virtual_mfa_device(self, VirtualMFADeviceName, Path):
        return {"VirtualMFADevice": {"Base32Secret": "JBSWY3DPEHPK3PXP", "SerialNumber": "arn:mfa:serial"}}

    def enable_mfa_device(self, UserName, SerialNumber, AuthenticationCode1, AuthenticationCode2):
        return {}

    def list_access_keys(self, UserName):
        # Note: Code references 'AccessKeyMetaData' (typo) so keep empty
        return {"AccessKeyMetaData": []}

    def get_access_key_last_used(self, AccessKeyId):
        return {"AccessKeyLastUsed": {"LastUsedDate": datetime.now(timezone.utc)}}

    def get_account_summary(self):
        return {"SummaryMap": {"AccountRootUser": "arn:aws:iam::123456789012:root"}}

    def detach_user_policy(self, UserName, PolicyArn):
        return {}

    # Role policy inspection for lambda_scanner
    def list_attached_role_policies(self, RoleName):
        return {"AttachedPolicies": [{"PolicyArn": "arn:policy", "PolicyName": "Permissive"}]}


class LambdaClient:
    def list_functions(self):
        return {"Functions": [{
            "FunctionName": "fn1",
            "Timeout": 120,
            "TracingConfig": {"Mode": "PassThrough"},
            "Role": "arn:aws:iam::123456789012:role/lambda-role",
            "KmsKeyArn": None,
        }]}

    def update_function_configuration(self, FunctionName, **kwargs):
        return {}


class SSMClient:
    def list_documents(self):
        return {"DocumentIdentifiers": [{"Name": "Doc1"}]}

    def describe_document_permission(self, Name, PermissionType):
        return {"AccountIds": ["All"]}

    def modify_document_permission(self, Name, PermissionType, AccountIdsToRemove):
        return {}

    def get_document(self, Name):
        return {"Name": Name}

    def update_document(self, Content, Name, DocumentVersion, DocumentFormat):
        return {}

    def list_compliance_summaries(self):
        return {"ComplianceSummaryItems": []}

    def create_patch_baseline(self, **kwargs):
        return {"BaselineId": "pb-123"}

    def describe_patch_baselines(self):
        return {"BaselineIdentities": [{"BaselineId": "pb-123"}]}

    def register_patch_baseline_for_patch_group(self, BaselineId, PatchGroup):
        return {}

    def add_tags_to_resource(self, ResourceType, ResourceId, Tags):
        return {}


class LogsClient:
    def create_log_group(self, logGroupName):
        return {}


class SNSClient:
    def list_topics(self):
        return {"Topics": [{"TopicArn": "arn:aws:sns:us-east-1:123456789012:topic1"}]}

    def get_topic_attributes(self, TopicArn):
        policy = '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":"*","Action":"sns:Publish","Resource":"*"}]}'
        return {"Attributes": {"Policy": policy}}

    def set_topic_attributes(self, TopicArn, AttributeName, AttributeValue):
        return {}

    def list_subscriptions_by_topic(self, TopicArn):
        return {"Subscriptions": [{"SubscriptionArn": "PendingConfirmation"}]}


class SQSClient:
    def list_queues(self):
        return {"QueueUrls": ["https://sqs.us-east-1.amazonaws.com/123456789012/q1"]}

    def get_queue_attributes(self, QueueUrl, AttributeNames):
        return {"Attributes": {"Policy": '{"Statement":[{"Principal":"*"}]}'}}

    def set_queue_attributes(self, QueueUrl, Attributes):
        return {}

    def get_queue_url(self, QueueName):
        return {"QueueUrl": f"https://sqs.us-east-1.amazonaws.com/123456789012/{QueueName}"}


class STSClient:
    def get_caller_identity(self):
        return {"Account": "123456789012"}


class KMSClient:
    def list_keys(self):
        return {"Keys": []}

    def create_key(self, **kwargs):
        return {"KeyMetadata": {"KeyId": "key-123"}}


class RDSClient:
    def describe_db_instances(self):
        return {"DBInstances": [{
            "DBInstanceIdentifier": "db1",
            "PubliclyAccessible": True,
            "StorageEncrypted": False,
            "BackupRetentionPeriod": 0,
            "DeletionProtection": False,
        }]}

    def modify_db_instance(self, **kwargs):
        return {}


def test_all_scanners_check_runs():
    # Imports after sys.path injection
    from scanner.aws import (
        s3_scanner,
        iam_scanner,
        ec2_scanner,
        rds_scanner,
        cloudtrail_scanner,
        cloudwatch_scanner,
        elb_scanner,
        ebs_scanner,
        lambda_scanner,
        ssm_scanner,
        sns_scanner,
        sqs_scanner,
    )

    session = MockSession()
    logger = DummyLogger()

    scanners = [
        s3_scanner,
        iam_scanner,
        ec2_scanner,
        rds_scanner,
        cloudtrail_scanner,
        cloudwatch_scanner,
        elb_scanner,
        ebs_scanner,
        lambda_scanner,
        ssm_scanner,
        sns_scanner,
        sqs_scanner,
    ]

    for mod in scanners:
        mod.check(session=session, logger=logger, dry_run=True, policy={})
