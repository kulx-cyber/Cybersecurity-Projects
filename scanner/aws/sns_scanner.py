import json
import boto3
from botocore.exceptions import ClientError

def check(session, logger, dry_run, policy):
    sns_client = session.client("sns")
    topics = sns_client.list_topics().get("Topics", [])

    for topic in topics:
        arn = topic.get("TopicArn")
        try:
            attrs = sns_client.get_topic_attributes(TopicArn=arn).get("Attributes", {})
        except ClientError as e:
            logger.error(f"Failed to get attributes for topic {arn}: {e}")
            continue

        if policy.get("public_access", True):
            if "Policy" in attrs and '"AWS":"*"' in attrs.get("Policy", ""):
                logger.warning(f"Topic {arn} is publicly accessible.")
                if not dry_run:
                    try:
                        policy_json = json.loads(attrs.get("Policy", "{}"))
                        original_count = len(policy_json.get("Statement", []))
                        policy_json["Statement"] = [
                            stmt for stmt in policy_json.get("Statement", [])
                            if not (stmt.get("Principal") == "*" or stmt.get("Principal", {}).get("AWS") == "*")
                        ]
                        if len(policy_json["Statement"]) < original_count:
                            sns_client.set_topic_attributes(
                                TopicArn=arn,
                                AttributeName="Policy",
                                AttributeValue=json.dumps(policy_json)
                            )
                            logger.info(f"Removed public access from topic {arn}.")
                        else:
                            logger.info(f"No public access policy found to remove on topic {arn}.")
                    except Exception as e:
                        logger.error(f"Failed to remediate public access on topic {arn}: {e}")

        if policy.get("encryption", True):
            if "KmsMasterKeyId" not in attrs:
                logger.warning(f"Topic {arn} does not have encryption enabled.")
                if not dry_run:
                    try:
                        kms_key_arn = policy.get("kms_key_arn")
                        if not kms_key_arn:
                            # Use AWS managed key alias for SNS by default
                            region = session.region_name
                            account_id = session.client("sts").get_caller_identity()["Account"]
                            kms_key_arn = f"arn:aws:kms:{region}:{account_id}:alias/aws/sns"
                        sns_client.set_topic_attributes(
                            TopicArn=arn,
                            AttributeName="KmsMasterKeyId",
                            AttributeValue=kms_key_arn
                        )
                        logger.info(f"Enabled encryption on topic {arn} using key {kms_key_arn}.")
                    except Exception as e:
                        logger.error(f"Failed to enable encryption on topic {arn}: {e}")

        #3. Subscription checks
        if policy.get("subscriptions_confirmation", True):
            subs = sns_client.list_subscriptions_by_topic(TopicArn=arn).get("Subscriptions", [])
            for sub in subs:
                if sub.get("SubscriptionArn") == "PendingConfirmation":
                    logger.warning(f"Subscription to {arn} not confirmed.")
                    if not dry_run:
                        logger.warning(f"Cannot unsubscribe a pending confirmation subscription.")
