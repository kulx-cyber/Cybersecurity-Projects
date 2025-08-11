import boto3
from botocore.exceptions import ClientError

def check(session, logger, dry_run, policy):
    s3_client = session.client("s3")
    logger.info("Starting S3 bucket checks...")

    try:
        buckets = s3_client.list_buckets()
        logger.info(f"Found {len(buckets.get('Buckets', []))} S3 buckets.")
    except ClientError as e:
        logger.error(f"Error listing S3 buckets: {e}")
        return

    for bucket in buckets['Buckets']:
        bucket_name = bucket['Name']
        logger.info(f"Checking bucket: {bucket_name}")

        # 1. Block public access via PublicAccessBlock
        if policy.get("public_access", True):
            try:
                pab = s3_client.get_public_access_block(Bucket=bucket_name).get('PublicAccessBlockConfiguration', {})
            except ClientError as e:
                code = e.response.get('Error', {}).get('Code')
                if code in ('NoSuchPublicAccessBlockConfiguration', 'NoSuchPublicAccessBlock'):  # different SDKs
                    pab = {}
                else:
                    logger.error(f"Error getting PublicAccessBlock for bucket {bucket_name}: {e}")
                    pab = {}

            desired = {
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
            if any(pab.get(k) is not True for k in desired.keys()):
                logger.warning(f"Bucket {bucket_name} does not fully block public access.")
                if dry_run:
                    logger.info(f"Dry run: Would enable S3 PublicAccessBlock on bucket {bucket_name}.")
                else:
                    try:
                        s3_client.put_public_access_block(
                            Bucket=bucket_name,
                            PublicAccessBlockConfiguration=desired
                        )
                        logger.info(f"Enabled S3 PublicAccessBlock on bucket {bucket_name}.")
                    except ClientError as e:
                        logger.error(f"Failed to set PublicAccessBlock on bucket {bucket_name}: {e}")

        # 2. Default encryption
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
                        try:
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
                            logger.info(f"Enabled default encryption for bucket {bucket_name}.")
                        except ClientError as e:
                            logger.error(f"Failed to enable encryption for bucket {bucket_name}: {e}")
                else:
                    logger.error(f"Error getting encryption for bucket {bucket_name}: {e}")

        # 3. Versioning
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
                        try:
                            s3_client.put_bucket_versioning(
                                Bucket=bucket_name,
                                VersioningConfiguration={'Status': 'Enabled'}
                            )
                            logger.info(f"Enabled versioning for bucket {bucket_name}.")
                        except ClientError as e:
                            logger.error(f"Failed to enable versioning for bucket {bucket_name}: {e}")
            except ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchBucket':
                    logger.warning(f"Bucket {bucket_name} does not exist.")
                else:
                    logger.error(f"Error getting versioning for bucket {bucket_name}: {e}")

        # 4. Server access logging
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
                        log_bucket_name = policy.get('s3_log_bucket')
                        if not log_bucket_name:
                            logger.warning("No 's3_log_bucket' specified in policy; skipping auto-enabling access logs.")
                        else:
                            try:
                                # Ensure target exists
                                s3_client.head_bucket(Bucket=log_bucket_name)
                                s3_client.put_bucket_logging(
                                    Bucket=bucket_name,
                                    BucketLoggingStatus={
                                        'LoggingEnabled': {
                                            'TargetBucket': log_bucket_name,
                                            'TargetPrefix': f"{bucket_name}/"
                                        }
                                    }
                                )
                                logger.info(f"Enabled access logging for bucket {bucket_name} to {log_bucket_name}.")
                            except ClientError as e:
                                logger.error(f"Failed to enable logging for {bucket_name}: {e}")
            except ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchBucket':
                    logger.warning(f"Bucket {bucket_name} does not exist.")
                else:
                    logger.error(f"Error getting logging for bucket {bucket_name}: {e}")

    # 5. Ensure BlockPublicPolicy flag (subset of PAB) - handled above with desired PAB config.