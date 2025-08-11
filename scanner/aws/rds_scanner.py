import boto3
from botocore.exceptions import ClientError


def check(session, logger, dry_run, policy):
    rds_client = session.client("rds")
    logger.info("Starting RDS policy checks...")

    try:
        instances = rds_client.describe_db_instances().get('DBInstances', [])
        logger.info(f"Found {len(instances)} RDS instances.")
    except ClientError as e:
        logger.error(f"Error listing RDS instances: {e}")
        return

    for db in instances:
        db_id = db.get('DBInstanceIdentifier')

        # 1. Public Accessibility
        if policy.get('public_access', True):
            if db.get('PubliclyAccessible'):
                logger.warning(f"RDS instance {db_id} is publicly accessible.")
                if not dry_run:
                    try:
                        rds_client.modify_db_instance(
                            DBInstanceIdentifier=db_id,
                            PubliclyAccessible=False,
                            ApplyImmediately=True
                        )
                        logger.info(f"Disabled public accessibility on RDS instance {db_id}.")
                    except ClientError as e:
                        logger.error(f"Failed to modify public access for {db_id}: {e}")

        # 2. Storage Encryption Check (cannot be enabled in-place post-creation)
        if policy.get('storage_encryption', True):
            if not db.get('StorageEncrypted', False):
                logger.warning(f"RDS instance {db_id} does not have storage encryption enabled. Requires snapshot-copy-and-restore to remediate.")

        # 3. Backup Retention Period
        if policy.get('backup_retention', True):
            retention_period = db.get('BackupRetentionPeriod', 0)
            req_days = max(1, int(policy.get('backup_retention_days', 7)))
            if retention_period < req_days:
                logger.warning(f"RDS instance {db_id} has backup retention {retention_period} < {req_days} days.")
                if not dry_run:
                    try:
                        rds_client.modify_db_instance(
                            DBInstanceIdentifier=db_id,
                            BackupRetentionPeriod=req_days,
                            ApplyImmediately=True
                        )
                        logger.info(f"Updated backup retention to {req_days} days for {db_id}.")
                    except ClientError as e:
                        logger.error(f"Failed to update backup retention for {db_id}: {e}")

        # 4. Deletion Protection
        if policy.get('deletion_protection', True):
            if not db.get('DeletionProtection', False):
                logger.warning(f"RDS instance {db_id} does not have deletion protection enabled.")
                if not dry_run:
                    try:
                        rds_client.modify_db_instance(
                            DBInstanceIdentifier=db_id,
                            DeletionProtection=True,
                            ApplyImmediately=True
                        )
                        logger.info(f"Enabled deletion protection for {db_id}.")
                    except ClientError as e:
                        logger.error(f"Failed to enable deletion protection for {db_id}: {e}")