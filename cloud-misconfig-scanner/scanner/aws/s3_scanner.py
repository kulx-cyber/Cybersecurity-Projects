import boto3
from botocore.exceptions import ClientError

def check(session, logger, dry_run, policy):
    s3_client = session.client("s3")
    logger.info("Starting S3 bucket checks...")

    try:
        buckets = s3_client.list_buckets()
        logger.info(f"Found {len(buckets['Buckets'])} S3 buckets.")
    except ClientError as e:
        logger.error(f"Error listing S3 buckets: {e}")
        return

    for bucket in buckets['Buckets']:
        bucket_name = bucket['Name']
        logger.info(f"Checking bucket: {bucket_name}")

        # 1. Check Public Access
        if policy.get("public_access", True):
            try:
                block_public = s3_client.get_bucket_policy_status(Bucket=bucket_name)
                is_public = block_public['PolicyStatus']['IsPublic']

                if is_public:
                    logger.warning(f"Bucket {bucket_name} has a public policy.")

                    if dry_run:
                        logger.info(f"Dry run: Would block public access for bucket {bucket_name}.")
                    else:
                        s3_client.put_bucket_policy(
                            Bucket=bucket_name,
                            PublicAccessBlockConfiguration={
                                'BlockPublicAcls': True,
                                'IgnorePublicAcls': True,
                                'BlockPublicPolicy': True,
                                'RestrictPublicBuckets': True
                            }
                        )
                        logger.info(f"Blocked public access for bucket {bucket_name}.")
                else:
                    logger.info(f"Bucket {bucket_name} has a private policy.")

            except ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
                    logger.warning(f"Bucket {bucket_name} has no policy.")
                else:
                    logger.error(f"Error getting policy for bucket {bucket_name}: {e}")

        # Check for encryption
        #if policy.get("enforce_encryption", True):