import boto3
from botocore.exceptions import ClientError

def check(session, logger, dry_run, policy):
    lambda_client = session.client("lambda")
    logger.info("Starting Lambda policy checks...")

    try:
        functions = lambda_client.list_functions().get('Functions', [])
        logger.info(f"Found {len(functions)} Lambda functions.")
    except ClientError as e:
        logger.error(f"Error listing Lambda functions: {e}")
        return
    
    for function in functions:
        fn_name = function['FunctionName']
        logger.info(f"Checking function: {fn_name}")

        #1. Timeout Configuration
        if policy.get('function_timeout', True):
            if function["Timeout"] > 60:
                logger.warning(f"Lambda function {fn_name} has a timeout greater than 60 seconds.")
                '''
                if not dry_run:
                    lambda_client.update_function_configuration(
                        FunctionName=fn_name,
                        Timeout=60
                    )
                    logger.info(f"Updated timeout for Lambda function {fn_name} to 60 seconds.")
                '''
        
        #2. logging_enabled
        if policy.get('logging_enabled', True):
            if not function.get('TracingConfig', {}).get('Mode') == 'Active':
                logger.warning(f"Lambda function {fn_name} does not have active tracing enabled.")
                '''
                if not dry_run:
                    lambda_client.put_function_concurrency(
                        FunctionName=fn_name,
                        TracingConfig={'Mode': 'Active'}
                    )
                    logger.info(f"Enabled active tracing for Lambda function {fn_name}.")
                '''
        
        #4. Overly permissive policies
        if policy.get('over_permissioned_role', True):
            role_arn = function.get('Role')
            if role_arn:
                try:
                    role_name = role_arn.split('/')[-1]
                    role = lambda_client.get_role(RoleName=role_name)
                    policies = role.get ('Role', {}).get('AssumeRolePolicyDocument', {}).get('Statement', [])
                    for policy in policies: 
                        if policy.get('Effect') == 'Allow' and (policy.get('Action') == '*' or policy.get('Resource') == '*'):
                            logger.warning(f"Lambda function {fn_name} has overly permissive role: {role_arn}")
                            if not dry_run:
                                lambda_client.delete_role(RoleName=role_name)
                                logger.info(f"Deleted overly permissive role {role_name} for Lambda function {fn_name}.")
                except ClientError as e:
                    logger.error(f"Error checking role for Lambda function {fn_name}: {e}")

        #5. Environment Variables Encryption
        if policy.get('environment_variables_encrypted', True):
            if not function.get('KmsKeyArn'):
                logger.warning(f"Lambda function {fn_name} does not have environment variables encrypted.")
                '''
                if not dry_run:
                    lambda_client.update_function_configuration(
                        FunctionName=fn_name,
                        KmsKeyArn='arn:aws:kms:REGION:ACCOUNT_ID:key/KEY_ID'
                    )
                    logger.info(f"Enabled environment variables encryption for Lambda function {fn_name}.")
                '''