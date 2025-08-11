import boto3
from botocore.exceptions import ClientError
import json

def check(session, logger, dry_run, policy):
    sqs_client = session.client("sqs")
    queues = sqs_client.list_queues().get("QueueUrls", [])

    for q in queues:
        queue_name = q.split('/')[-1]
        attrs = sqs_client.get_queue_attributes(QueueUrl=q, AttributeNames=["All"])["Attributes"]

        if policy.get("server_side_encryption", True) and "KmsMasterKeyId" not in attrs:
            logger.warning(f"SQS Queue {queue_name} not encrypted.")
            if not dry_run:
                try:
                    sqs_client.set_queue_attributes(
                        QueueUrl=q,
                        Attributes={
                            'KmsMasterKeyId': 'alias/aws/sqs',  # Use AWS managed key
                            'KmsDataKeyReusePeriodSeconds': '300'
                        }
                    )
                    logger.info(f"Enabled encryption for queue {queue_name}.")
                except ClientError as e:
                    logger.error(f"Failed to enable encryption for queue {queue_name}: {e}")
            else:
                logger.info(f"Dry run: Would enable encryption for queue {queue_name}.")

        if policy.get("public_access", True):
            if "Policy" in attrs and '"Principal":"*"' in attrs["Policy"]:
                logger.warning(f"SQS Queue {queue_name} has public access.")
                if not dry_run:
                    try:
                        # Create a restrictive policy
                        account_id = session.client('sts').get_caller_identity()['Account']
                        restricted_policy = {
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Principal": {
                                        "AWS": f"arn:aws:iam::{account_id}:root"
                                    },
                                    "Action": "sqs:*",
                                    "Resource": f"arn:aws:sqs:*:{account_id}:{queue_name}"
                                }
                            ]
                        }
                        
                        sqs_client.set_queue_attributes(
                            QueueUrl=q,
                            Attributes={
                                'Policy': json.dumps(restricted_policy)
                            }
                        )
                        logger.info(f"Removed public access from queue {queue_name}.")
                    except ClientError as e:
                        logger.error(f"Failed to remove public access from queue {queue_name}: {e}")
                else:
                    logger.info(f"Dry run: Would remove public access from queue {queue_name}.")

        if policy.get("dead_letter_queue_configured", True):
            if "RedrivePolicy" not in attrs:
                logger.warning(f"SQS Queue {queue_name} has no DLQ configured.")
                if not dry_run:
                    try:
                        # Create DLQ name
                        dlq_name = f"{queue_name}-dlq"
                        
                        # Check if DLQ already exists, if not create it
                        try:
                            dlq_response = sqs_client.get_queue_url(QueueName=dlq_name)
                            dlq_url = dlq_response['QueueUrl']
                            logger.info(f"Using existing DLQ: {dlq_name}")
                        except ClientError:
                            # Create new DLQ
                            dlq_response = sqs_client.create_queue(
                                QueueName=dlq_name,
                                Attributes={
                                    'MessageRetentionPeriod': '1209600',  # 14 days
                                    'VisibilityTimeoutSeconds': '60'
                                }
                            )
                            dlq_url = dlq_response['QueueUrl']
                            logger.info(f"Created new DLQ: {dlq_name}")
                        
                        # Get DLQ ARN
                        dlq_attrs = sqs_client.get_queue_attributes(
                            QueueUrl=dlq_url,
                            AttributeNames=['QueueArn']
                        )
                        dlq_arn = dlq_attrs['Attributes']['QueueArn']
                        
                        # Configure redrive policy
                        redrive_policy = {
                            "deadLetterTargetArn": dlq_arn,
                            "maxReceiveCount": 3
                        }
                        
                        sqs_client.set_queue_attributes(
                            QueueUrl=q,
                            Attributes={
                                'RedrivePolicy': json.dumps(redrive_policy)
                            }
                        )
                        logger.info(f"Configured DLQ for queue {queue_name}.")
                    except ClientError as e:
                        logger.error(f"Failed to configure DLQ for queue {queue_name}: {e}")
                else:
                    logger.info(f"Dry run: Would configure DLQ for queue {queue_name}.")
