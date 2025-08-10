import boto3
from botocore.exceptions import ClientError

def check(session, logger, dry_run, policy):
    sns_client = session.client("sns")
    topics = sns_client.list_topics()["Topics"]

    for topic in topics:
        arn = topic["TopicArn"]

        if policy.get("public_access", True):
            attrs = sns_client.get_topic_attributes(TopicArn=arn)["Attributes"]
            if "Policy" in attrs and '"AWS":"*"' in attrs["Policy"]:
                logger.warning(f"Topic {arn} is publicly accessible.")

        if policy.get("encryption", True):
            if "KmsMasterKeyId" not in attrs:
                logger.warning(f"Topic {arn} does not have encryption enabled.")

        if policy.get("subscriptions_confirmation", True):
            subs = sns_client.list_subscriptions_by_topic(TopicArn=arn)["Subscriptions"]
            for sub in subs:
                if sub["SubscriptionArn"] == "PendingConfirmation":
                    logger.warning(f"Subscription to {arn} not confirmed.")
