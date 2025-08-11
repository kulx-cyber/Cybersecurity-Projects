import boto3
from botocore.exceptions import ClientError
import datetime
import pyotp

def check(session, logger, dry_run, policy):
    iam_client = session.client("iam")
    logger.info("Starting IAM policy checks...")

    try:
        users = iam_client.list_users()['Users']
        logger.info(f"Found {len(users)} IAM users.")
    except ClientError as e:
        logger.error(f"Error listing IAM users: {e}")
        return
    
    for user in users:
        user_name =  user['UserName']
        logger.info(f"Checking user: {user_name}")
        
        #1. Inline policies
        if policy.get('inline_policies', True):
            inline_policies = iam_client.list_user_policies(UserName=user_name)['PolicyNames']
            if inline_policies:
                logger.warning(f"User {user_name} has inline policies: {inline_policies}")
                if not dry_run:
                    for policy_name in inline_policies:
                        iam_client.delete_user_policy(UserName=user_name, PolicyName=policy_name)
                        logger.info(f"Deleted inline policy {policy_name} for user {user_name}")
        
        #2.Overly permissive policies
        if policy.get('overly_permissive', True):
            attached_policies = iam_client.list_attached_user_policies(UserName=user_name)['AttachedPolicies']
            for p in attached_policies:
                policy_arn = p['PolicyArn']
                policy_meta = iam_client.get_policy(PolicyArn=policy_arn)['Policy']
                version_id = policy_meta['DefaultVersionId']
                document = iam_client.get_policy_version(PolicyArn=policy_arn, VersionId=version_id)['PolicyVersion']['Document']
                for statement in document.get('Statement', []):
                    if statement in document.get('Statement', []):
                        if statement.get('Effect') == 'Allow' and (statement.get('Action') == '*' or statement.get('Resource') == '*'):
                            logger.warning(f"User {user_name} has overly permissive policy: {policy_arn}")
                            if not dry_run:
                                iam_client.detach_user_policy(UserName=user_name, PolicyArn=policy_arn)
                                logger.info(f"Detached overly permissive policy {policy_arn} from user {user_name}")

        #3 Password Policy
        if (policy.get('password_policy', True)):
            try:
                password_policy = iam_client.get_account_password_policy()['PasswordPolicy']
                if not password_policy.get('RequiredSymbols', True) or \
                    not password_policy.get('MinimumPasswordLength', 8) or \
                        not password_policy.get('RequireUppercaseCharacters', True) or \
                            not password_policy.get('RequireLowercaseCharacters', True) or \
                                not password_policy.get('RequireNumbers', True):
                                    logger.warning(f"User {user_name} does not meet the password policy requirements.")
                if not dry_run:
                    iam_client.update_account_password_policy(
                        RequireUppercaseCharacters=True,
                        RequireLowercaseCharacters=True,
                        RequireNumbers=True,
                        RequireSymbols=True,
                        MinimumPasswordLength=8
                    )
                    logger.info(f"Updated password policy for user {user_name}.")
            except ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchEntity':
                    logger.warning(f"User {user_name} does not have a password policy set.")
                else:
                    logger.error(f"Error checking password policy for user {user_name}: {e}")

        #4 MFA (Multi-Factor Authentication) Enabled
        if policy.get('mfa_enabled', True):
            try:
                mfa = iam_client.list_mfa_devices(UserName=user_name)['MFADevices']
                if not mfa: 
                    logger.warning(f"User {user_name} does not have MFA enabled.")
                if not dry_run:
                    #Step 1: Create a new virutal MFA device
                    logger.info(f"Creating virtual MFA device for user {user_name}")

                    #Step 2: Create the virtual MFA device
                    create_mfa_response = iam_client.create_virtual_mfa_device(
                        VirtualMFADeviceName=f"{user_name}_mfa",
                        Path=f"/users/{user_name}/"
                    )

                    #Step 3: REtrive the secret code and QR code information
                    secret_code = create_mfa_response['VirtualMFADevice']['Base32Secret']
                    serial_number = create_mfa_response['VirtualMFADevice']['SerialNumber']
                    logger.info(f"Created virtual MFA device for {user_name}. Serial Number: {serial_number}")
                    logger.info(f"Secret Code for MFA device: {secret_code}")

                    # Step 4: Generate a QR Code (optional)
                    # You can use this secret code to generate a QR code using a library like `pyotp`
                    otp = pyotp.TOTP(secret_code)
                    logger.info(f"To link MFA device, scan this QR code with your MFA app: {otp.provisioning_uri(user_name, issuer_name='MyCompany')}")
                    logger.info("The user should scan the QR code with their MFA app (Google Authenticator, etc.).")

                    # Step 5: Prompt user for the two consecutive MFA codes
                    authentication_code_1 = input("Enter MFA Code 1 (from MFA app): ")
                    authentication_code_2 = input("Enter MFA Code 2 (from MFA app): ")

                    # Step 6: Enable the MFA device using the generated codes
                    enable_mfa_response = iam_client.enable_mfa_device(
                        UserName=user_name,
                        SerialNumber=serial_number,
                        AuthenticationCode1=authentication_code_1,
                        AuthenticationCode2=authentication_code_2
                    )

                    logger.info(f"Enabled MFA for user {user_name}.")
            except ClientError as e:
                logger.error(f"Error enabling MFA for user {user_name}: {e}")

        #5. Unused AccessKeys
        if policy.get('unused_access_keys', True):
            try:
                access_keys = iam_client.list_access_keys(UserName=user_name).get('AccessKeyMetaData', [])
                for key in access_keys:
                    key_id = key['AccessKeyId']
                    last_used = iam_client.get_access_key_last_used(AccessKeyId=key_id)['AccessKeyLastUsed']
                    if 'LastUsedDate' in last_used:
                        days_unused = (datetime.datetime.now(datetime.timezone.utc) - last_used['LastUsedDate']).days
                        if days_unused > 90:  # Assuming 90 days of inactivity
                            logger.warning(f"User {user_name} has an unused access key: {key_id} (last used {days_unused} days ago)")
                            if not dry_run:
                                iam_client.delete_access_key(UserName=user_name, AccessKeyId=key_id)
                                logger.info(f"Deleted unused access key {key_id} for user {user_name}.")
            except ClientError as e:
                logger.error(f"Error checking unused access keys for user {user_name}: {e}")

        #6 Root Account Usage
        if policy.get('root_account_access', True):
            try:
                root_account = iam_client.get_account_summary().get('SummaryMap', {}).get('AccountRootUser')
                if root_account:
                    logger.warning(f"User {user_name} has root account access: {root_account}")
                if not dry_run:
                    iam_client.detach_user_policy(UserName=user_name, PolicyArn=root_account)
                    logger.info(f"Detached root account access from user {user_name}.")
            except ClientError as e:
                logger.error(f"Error checking root account access for user {user_name}: {e}")
