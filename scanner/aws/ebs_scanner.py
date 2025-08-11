import boto3
from botocore.exceptions import ClientError

def check(session, logger, dry_run, policy):
    ebs_client = session.client("ec2")
    logger.info("Starting EBS volume checks...")

    #1. Check for volume encryption and unused volumes
    if policy.get("volume_encryption", True) or policy.get("unused_volumes", True):
        try:
            volumes = ebs_client.describe_volumes().get('Volumes', [])
            logger.info(f"Found {len(volumes)} EBS volumes.")
        except ClientError as e:
            logger.error(f"Error describing EBS volumes: {e}")
            return

        for vol in volumes:
            volumeId = vol.get('VolumeId')
            logger.info(f"Checking volume: {volumeId}")

            if not vol.get('Encrypted', False):
                logger.warning(f"EBS Volume {volumeId} is not encrypted.")
                if not dry_run:
                    logger.info(f"Remediation: Consider replacing or encrypting volume {volumeId} manually.")

            if vol.get('State') == 'available':
                logger.warning(f"EBS Volume {volumeId} is not attached to any instance.")
                if not dry_run:
                    try:
                        ebs_client.delete_volume(VolumeId=volumeId)
                        logger.info(f"Deleted unused EBS Volume {volumeId}.")   
                    except ClientError as e:
                        logger.error(f"Error deleting EBS Volume {volumeId}: {e}")

    #2. Check for snapshots public access
    if policy.get("snapshot_public_access", True):
        try:
            snapshots = ebs_client.describe_snapshots(OwnerIds=['self']).get('Snapshots', [])
            logger.info(f"Found {len(snapshots)} EBS snapshots.")
        except ClientError as e:
            logger.error(f"Error describing EBS snapshots: {e}")
            return

        for snap in snapshots:
            snapshotId = snap.get('SnapshotId')
            logger.info(f"Checking snapshot: {snapshotId}")
            attr = ebs_client.describe_snapshot_attribute(
                SnapshotId=snapshotId,
                Attribute='createVolumePermission'
            )
            permissions = attr.get('CreateVolumePermissions', [])
            for perm in permissions:
                if 'Group' in perm and perm.get('Group') == 'all':
                    logger.warning(f"EBS Snapshot {snapshotId} is publicly accessible.")
                    if not dry_run:
                        try:
                            ebs_client.modify_snapshot_attribute(
                                SnapshotId=snapshotId,
                                Attribute='createVolumePermission',
                                OperationType='remove',
                                GroupNames=['all']
                            )
                            logger.info(f"Removed public access from EBS Snapshot {snapshotId}.")
                        except ClientError as e:
                            logger.error(f"Error modifying EBS Snapshot {snapshotId}: {e}")
