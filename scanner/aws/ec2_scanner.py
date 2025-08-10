import boto3
from botocore.exceptions import ClientError

def check(session, logger, dry_run, policy):
    ec2_client = session.client("ec2")
    logger.info("Starting EC2 policy checks...")

    try:
        #1. unrestricted ssh access and insecure security groups
        if policy.get('unrestricted_ssh', True) or policy.get('insecure_security_groups', True):
            security_groups = ec2_client.describe_security_groups().get('SecurityGroups', [])
            logger.info(f"Found {len(security_groups)} security groups.")
            for sg in security_groups:
                if sg.get('IpPermissions'):
                    for permission in sg.get('IpPermissions', []):
                        for ip_range in permission.get('IpRanges', []):
                            cidr = ip_range.get('CidrIp', '')
                            if cidr == '0.0.0.0/0':
                                from_port = permission.get('FromPort')
                                to_port = permission.get('ToPort')
                                if from_port == 22 and to_port == 22 and policy.get('unrestricted_ssh', True):
                                    logger.warning(f"Security group {sg['GroupId']} allows unrestricted SSH access.")
                                    if not dry_run:
                                        ec2_client.revoke_security_group_ingress(
                                            GroupId=sg['GroupId'],
                                            IpPermissions=[permission]
                                        )
                                elif policy.get('insecure_security_groups', True):
                                    logger.warning(f"Security group {sg['GroupId']} allows insecure access.")
                                    if not dry_run:
                                        ec2_client.revoke_security_group_ingress(
                                            GroupId=sg['GroupId'],
                                            IpPermissions=[permission]
                                        )
        #2. metadata http tokens
        if policy.get('metadata_http_tokens', True):
            instances = ec2_client.describe_instances().get('Reservations', [])
            instance_count = sum(len(reservation.get('Instances', [])) for reservation in instances)
            logger.info(f"Found {instance_count} EC2 instances.")
            for reservation in instances:
                for instance in reservation.get('Instances', []):
                    metadata_options = instance.get('MetadataOptions', {})
                    if metadata_options.get('HttpTokens') != 'required':
                        logger.warning(f"Instance {instance['InstanceId']} does not have metadata HTTP tokens set to 'required'.")
                        if not dry_run:
                            ec2_client.modify_instance_metadata_options(
                                InstanceId=instance['InstanceId'],
                                HttpTokens='required'
                            )
        
        #3. Public IPs assignment
        if policy.get('public_ip_assignment', True):
            instances = ec2_client.describe_instances().get('Reservations', [])
            for reservation in instances:
                for instance in reservation.get('Instances', []):
                    if instance.get('PublicIpAddress'):
                        logger.warning(f"Instance {instance['InstanceId']} has a public IP assigned.")
                        if not dry_run:
                            ec2_client.modify_instance_attribute(
                                InstanceId=instance['InstanceId'],
                                NoPublicIp=True
                            )

        #4. EBS volume encryption
        if policy.get('volume_encryption', True):
            volumes = ec2_client.describe_volumes().get('Volumes', [])
            for volume in volumes:
                if not volume.get('Encrypted'):
                    logger.warning(f"Volume {volume['VolumeId']} is not encrypted.")
                    if not dry_run:
                        ec2_client.modify_volume(
                            VolumeId=volume['VolumeId'],
                            KmsKeyId=policy.get('kms_key_id')
                        )
    except ClientError as e:
        logger.error(f"Error during EC2 checks: {e}")