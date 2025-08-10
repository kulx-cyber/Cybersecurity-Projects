import boto3
from botocore.exceptions import ClientError

def check(session, logger, dry_run, policy):
    cloudtrail_client = session.client("cloudtrail")
    logger.info("Starting CloudTrail policy checks...")

    try:
        trails = cloudtrail_client.describe_trails().get('trailList', [])
        logger.info(f"Found {len(trails)} CloudTrail trails.")
    except ClientError as e:
        logger.error(f"Error listing CloudTrail trails: {e}")
        return
    
    for trail in trails:
        #1. Ensure CloudTrail is enabled
        if policy.get('logging_enabled', True):
            try:
                status = cloudtrail_client.get_trail_status(Name=trail['Name'])
                if not status.get('IsLogging'):
                    logger.warning(f"CloudTrail {trail['Name']} is not logging.")
                    '''
                    if not dry_run:
                        cloudtrail_client.start_logging(Name=trail['Name'])
                        logger.info(f"Started logging for CloudTrail {trail['Name']}.")
                    '''
            except ClientError as e:
                logger.error(f"Error getting status for CloudTrail {trail['Name']}: {e}")

        #2. Multi-region trails
        if policy.get('multi_region', True):
            if not trail.get('IsMultiRegionTrail'):
                logger.warning(f"CloudTrail {trail['Name']} is not a multi-region trail.")
                '''
                if not dry_run:
                    cloudtrail_client.update_trail(
                        Name=trail['Name'],
                        IsMultiRegionTrail=True
                    )
                    logger.info(f"Updated CloudTrail {trail['Name']} to be multi-region.")
                '''
        
        #3. Log File Validation
        if policy.get('log_file_validation', True):
            if not trail.get('LogFileValidationEnabled'):
                logger.warning(f"CloudTrail {trail['Name']} does not have log file validation enabled.")
                '''
                if not dry_run:
                    cloudtrail_client.update_trail(
                        Name=trail['Name'],
                        LogFileValidationEnabled=True
                    )
                logger.info(f"Enabled log file validation for CloudTrail {trail['Name']}.")
                '''