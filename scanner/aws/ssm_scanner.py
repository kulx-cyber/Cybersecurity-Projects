import boto3
from botocore.exceptions import ClientError
import json

def check(session, logger, dry_run, policy):
    ssm_client = session.client("ssm")
    logger.info("Starting SSM checks...")

    if policy.get("document_permissions", True):
        try:
            docs = ssm_client.list_documents()["DocumentIdentifiers"]
            for doc in docs:
                try:
                    perms = ssm_client.describe_document_permission(Name=doc["Name"], PermissionType="Share")
                    if any(p == "All" for p in perms.get("AccountIds", [])):
                        logger.warning(f"Document {doc['Name']} is shared publicly.")
                        if not dry_run:
                            try:
                                # Remove public sharing by modifying document permissions
                                ssm_client.modify_document_permission(
                                    Name=doc["Name"],
                                    PermissionType="Share",
                                    AccountIdsToRemove=["All"]
                                )
                                logger.info(f"Removed public sharing from document {doc['Name']}.")
                            except ClientError as e:
                                logger.error(f"Failed to remove public sharing from document {doc['Name']}: {e}")
                        else:
                            logger.info(f"Dry run: Would remove public sharing from document {doc['Name']}.")
                except ClientError as e:
                    logger.error(f"Error checking permissions for document {doc['Name']}: {e}")
                    continue
        except ClientError as e:
            logger.error(f"Error listing SSM documents: {e}")

    if policy.get("session_logging", True):
        try:
            logs = ssm_client.get_document(Name="SSM-SessionManagerRunShell")
            if "CloudWatch" not in str(logs):
                logger.warning("SSM session logging not properly configured.")
                if not dry_run:
                    try:
                        # Create or update Session Manager preferences to enable logging
                        session_preferences = {
                            "sessionManagerRunShellConfig": {
                                "cloudWatchLogGroupName": "/aws/sessionmanager",
                                "cloudWatchEncryptionEnabled": True,
                                "s3BucketName": "",
                                "s3KeyPrefix": "",
                                "s3EncryptionEnabled": False
                            }
                        }
                        
                        # Create CloudWatch log group if it doesn't exist
                        cloudwatch_logs = session.client('logs')
                        try:
                            cloudwatch_logs.create_log_group(
                                logGroupName="/aws/sessionmanager"
                            )
                            logger.info("Created CloudWatch log group for Session Manager.")
                        except ClientError as e:
                            if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                                logger.error(f"Failed to create CloudWatch log group: {e}")
                        
                        # Update Session Manager preferences
                        ssm_client.update_document(
                            Content=json.dumps(session_preferences),
                            Name="SSM-SessionManagerRunShell",
                            DocumentVersion="$LATEST",
                            DocumentFormat="JSON"
                        )
                        logger.info("Enabled CloudWatch logging for Session Manager.")
                    except ClientError as e:
                        logger.error(f"Failed to configure session logging: {e}")
                else:
                    logger.info("Dry run: Would enable CloudWatch logging for Session Manager.")
        except ClientError as e:
            logger.error(f"Error checking session logging configuration: {e}")

    if policy.get("patch_compliance", True):
        try:
            compliance = ssm_client.list_compliance_summaries()["ComplianceSummaryItems"]
            if not compliance:
                logger.warning("No patch compliance info found.")
                if not dry_run:
                    try:
                        # Get all EC2 instances to register them for patch management
                        ec2_client = session.client('ec2')
                        instances = ec2_client.describe_instances()
                        
                        instance_ids = []
                        for reservation in instances['Reservations']:
                            for instance in reservation['Instances']:
                                if instance['State']['Name'] == 'running':
                                    instance_ids.append(instance['InstanceId'])
                        
                        if instance_ids:
                            # Create a patch baseline if none exists
                            try:
                                baseline_response = ssm_client.create_patch_baseline(
                                    Name="DefaultSecurityPatchBaseline",
                                    Description="Default security patch baseline for compliance scanning",
                                    OperatingSystem="AMAZON_LINUX_2",
                                    ApprovalRules={
                                        'PatchRules': [
                                            {
                                                'PatchFilterGroup': {
                                                    'PatchFilters': [
                                                        {
                                                            'Key': 'CLASSIFICATION',
                                                            'Values': ['Security', 'Bugfix', 'Critical']
                                                        }
                                                    ]
                                                },
                                                'ApproveAfterDays': 7,
                                                'EnableNonSecurity': False
                                            }
                                        ]
                                    }
                                )
                                baseline_id = baseline_response['BaselineId']
                                logger.info(f"Created patch baseline: {baseline_id}")
                            except ClientError as e:
                                if 'already exists' in str(e):
                                    # Get existing baseline
                                    baselines = ssm_client.describe_patch_baselines()
                                    baseline_id = baselines['BaselineIdentities'][0]['BaselineId']
                                    logger.info(f"Using existing patch baseline: {baseline_id}")
                                else:
                                    logger.error(f"Failed to create patch baseline: {e}")
                                    return
                            
                            # Register targets for patch management
                            try:
                                ssm_client.register_patch_baseline_for_patch_group(
                                    BaselineId=baseline_id,
                                    PatchGroup="DefaultPatchGroup"
                                )
                                
                                # Add instances to patch group using resource tags
                                for instance_id in instance_ids[:10]:  # Limit to first 10 instances
                                    try:
                                        ssm_client.add_tags_to_resource(
                                            ResourceType='ManagedInstance',
                                            ResourceId=instance_id,
                                            Tags=[
                                                {
                                                    'Key': 'Patch Group',
                                                    'Value': 'DefaultPatchGroup'
                                                }
                                            ]
                                        )
                                    except ClientError as tag_error:
                                        logger.warning(f"Could not tag instance {instance_id}: {tag_error}")
                                
                                logger.info(f"Registered {len(instance_ids)} instances for patch compliance monitoring.")
                            except ClientError as e:
                                logger.error(f"Failed to register patch targets: {e}")
                        else:
                            logger.info("No running EC2 instances found to register for patch compliance.")
                    except ClientError as e:
                        logger.error(f"Failed to configure patch compliance: {e}")
                else:
                    logger.info("Dry run: Would configure patch compliance monitoring.")
            else:
                logger.info(f"Found {len(compliance)} compliance summaries.")
        except ClientError as e:
            logger.error(f"Error checking patch compliance: {e}")

