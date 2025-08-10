import boto3
from botocore.exceptions import ClientError

def check(session, logger, dry_run, policy):
    sqs_client = session.client("sqs")
    queues = sqs_client.list_queues().get("QueueUrls", [])

    for q in queues:
        attrs = sqs_client.get_queue_attributes(QueueUrl=q, AttributeNames=["All"])["Attributes"]

        if policy.get("server_side_encryption", True) and "KmsMasterKeyId" not in attrs:
            logger.warning(f"SQS Queue {q} not encrypted.")

        if policy.get("public_access", True):
            if "Policy" in attrs and '"Principal":"*"' in attrs["Policy"]:
                logger.warning(f"SQS Queue {q} has public access.")

        if policy.get("dead_letter_queue_configured", True):
            if "RedrivePolicy" not in attrs:
                logger.warning(f"SQS Queue {q} has no DLQ configured.")
