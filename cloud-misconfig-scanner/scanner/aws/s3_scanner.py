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

        # 2. Check for encryption
        if policy.get("encryption_enabled", True):
            try:
                encryption = s3_client.get_bucket_encryption(Bucket=bucket_name)
                logger.info(f"Bucket {bucket_name} has encryption enabled: {encryption['ServerSideEncryptionConfiguration']}")
            except ClientError as e:
                if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                    logger.warning(f"Bucket {bucket_name} does not have encryption enabled.")
                    if dry_run:
                        logger.info(f"Dry run: Would enable encryption for bucket {bucket_name}.")
                    else:
                        s3_client.put_bucket_encryption(
                            Bucket=bucket_name,
                            ServerSideEncryptionConfiguration={
                                'Rules': [
                                    {
                                        'ApplyServerSideEncryptionByDefault': {
                                            'SSEAlgorithm': 'AES256'
                                        }
                                    }
                                ]
                            }
                        )
                        logger.info(f"Enabled encryption for bucket {bucket_name}.")
                else:
                    logger.error(f"Error getting encryption for bucket {bucket_name}: {e}")

        # 3. Check for versioning
        if policy.get("versioning_enabled", True):
            try:
                versioning = s3_client.get_bucket_versioning(Bucket=bucket_name)
                if versioning.get('Status') == 'Enabled':
                    logger.info(f"Bucket {bucket_name} has versioning enabled: {versioning}")
                else:
                    logger.warning(f"Bucket {bucket_name} does not have versioning enabled.")
                    if dry_run:
                        logger.info(f"Dry run: Would enable versioning for bucket {bucket_name}.")
                    else:
                        s3_client.put_bucket_versioning(
                            Bucket=bucket_name,
                            VersioningConfiguration={
                                'Status': 'Enabled'
                            }
                        )
                        logger.info(f"Enabled versioning for bucket {bucket_name}.")
            except ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchBucket':
                    logger.warning(f"Bucket {bucket_name} does not exist.")
                else:
                    logger.error(f"Error getting versioning for bucket {bucket_name}: {e}")

        # 4. Check for logging_enabled
        if policy.get("logging_enabled", True):
            try:
                logging = s3_client.get_bucket_logging(Bucket=bucket_name)
                if 'LoggingEnabled' in logging:
                    logger.info(f"Bucket {bucket_name} has logging enabled: {logging['LoggingEnabled']}")
                else:
                    logger.warning(f"Bucket {bucket_name} does not have logging enabled.")
                    if dry_run:
                        logger.info(f"Dry run: Would enable logging for bucket {bucket_name}.")
                    else:
                        s3_client.put_bucket_logging(
                            Bucket=bucket_name,
                            BucketLoggingStatus={
                                'LoggingEnabled': {
                                    'TargetBucket': 'your-log-bucket',
                                    'TargetPrefix': f"{bucket_name}/"
                                }
                            }
                        )
                        logger.info(f"Enabled logging for bucket {bucket_name}.")
            except ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchBucket':
                    logger.warning(f"Bucket {bucket_name} does not exist.")
                else:
                    logger.error(f"Error getting logging for bucket {bucket_name}: {e}")

        # 5. Check for block_public_policy policies
        if policy.get("block_public_policy", True):
            try:
                block_public = s3_client.get_public_access_block(Bucket=bucket_name)
                config = block_public.get('PublicAccessBlockConfiguration', {})
                if config.get('BlockPublicPolicy', False):
                    logger.info(f"Bucket {bucket_name} blocks public policies.")
                else:
                    logger.warning(f"Bucket {bucket_name} does not block public policies.")
                    if dry_run:
                        logger.info(f"Dry run: Would enable block public policy for bucket {bucket_name}.")
                    else:
                        config['BlockPublicPolicy'] = True
                        s3_client.put_public_access_block(
                            Bucket=bucket_name,
                            PublicAccessBlockConfiguration=config
                        )
                        logger.info(f"Enabled block public policy for bucket {bucket_name}.")
            except ClientError as e:
                logger.error(f"Error getting block public policy for bucket {bucket_name}: {e}")