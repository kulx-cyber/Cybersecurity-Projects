import boto3
from botocore.exceptions import ClientError

def check(session, logger, dry_run, policy):
    rds_client = session.client("rds")
    logger.info("Starting RDS policy checks...")

    try:
        instacnce = rds_client.describe_db_instances().get('DBInstances', [])
        logger.info(f"Found {len(instacnce)} RDS instances.")
    except ClientError as e:
        logger.error(f"Error listing RDS instances: {e}")
        return
    
    for db in instacnce:
        #1. Public Accessibility
        if policy.get('public_access', True):
            if db.get('PubliclyAccessible'):
                logger.warning(f"RDS instance {db['DBInstanceIdentifier']} is publicly accessible.")
                if not dry_run:
                    rds_client.modify_db_instance(
                        DBInstanceIdentifier=db['DBInstanceIdentifier'],
                        PubliclyAccessible=False
                    )
        
        #2. Storeage Encryptio Check
        if policy.get('storage_encryption', True):
            encrypted = db.get('StorageEncrypted', False)
            if not encrypted:
                logger.warning(f"RDS instance {db['DBInstanceIdentifier']} does not have storage encryption enabled.")
                '''
                if not dry_run:
                    rds_client.modify_db_instance(
                        DBInstanceIdentifier=db['DBInstanceIdentifier'],
                        StorageEncrypted=True
                    )
                '''

        #3. Backup Retention Period
        if policy.get('backup_retention', True):
            retention_period = db.get('BackupRetentionPeriod',0)
            if retention_period < 7:
                logger.warning(f"RDS instance {db['DBInstanceIdentifier']} has a backup retention period of {retention_period} days, which is less than the recommended 7 days.")
                '''
                if not dry_run:
                    rds_client.modify_db_instance(
                        DBInstanceIdentifier=db['DBInstanceIdentifier'],
                        BackupRetentionPeriod=7
                    )
                '''
        
        #4. Deletion Protection
        if policy.get('deletion_protection', True):
            delete_protection = db.get('DeletionProtection', False)
            if not delete_protection:
                logger.warning(f"RDS instance {db['DBInstanceIdentifier']} does not have deletion protection enabled.")
                '''
                if not dry_run:
                    rds_client.modify_db_instance(
                        DBInstanceIdentifier=db['DBInstanceIdentifier'],
                        DeletionProtection=True
                    )
                '''
