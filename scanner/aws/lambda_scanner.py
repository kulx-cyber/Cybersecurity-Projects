import boto3
from botocore.exceptions import ClientError


def check(session, logger, dry_run, policy):
    lambda_client = session.client("lambda")
    iam_client = session.client("iam")
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

        # 1. Timeout Configuration
        if policy.get('function_timeout', True):
            if function.get("Timeout", 0) > 60:
                logger.warning(f"Lambda function {fn_name} has a timeout greater than 60 seconds.")
                if not dry_run:
                    try:
                        lambda_client.update_function_configuration(
                            FunctionName=fn_name,
                            Timeout=60
                        )
                        logger.info(f"Updated timeout for Lambda function {fn_name} to 60 seconds.")
                    except ClientError as e:
                        logger.error(f"Failed to update timeout for {fn_name}: {e}")

        # 2. Tracing enabled (AWS X-Ray)
        if policy.get('tracing_enabled', True):
            if function.get('TracingConfig', {}).get('Mode') != 'Active':
                logger.warning(f"Lambda function {fn_name} does not have active tracing enabled.")
                if not dry_run:
                    try:
                        lambda_client.update_function_configuration(
                            FunctionName=fn_name,
                            TracingConfig={'Mode': 'Active'}
                        )
                        logger.info(f"Enabled active tracing for Lambda function {fn_name}.")
                    except ClientError as e:
                        logger.error(f"Failed to enable tracing for {fn_name}: {e}")

        # 3. Overly permissive role policies (detach wildcard policies)
        if policy.get('over_permissioned_role', True):
            role_arn = function.get('Role')
            if role_arn:
                role_name = role_arn.split('/')[-1]
                try:
                    attached = iam_client.list_attached_role_policies(RoleName=role_name).get('AttachedPolicies', [])
                    for ap in attached:
                        # Fetch default version of each attached policy
                        pol = iam_client.get_policy(PolicyArn=ap['PolicyArn'])['Policy']
                        ver = iam_client.get_policy_version(PolicyArn=ap['PolicyArn'], VersionId=pol['DefaultVersionId'])
                        doc = ver['PolicyVersion']['Document']
                        statements = doc['Statement'] if isinstance(doc['Statement'], list) else [doc['Statement']]
                        for stmt in statements:
                            actions = stmt.get('Action')
                            resources = stmt.get('Resource')
                            action_wild = (actions == '*' or (isinstance(actions, list) and '*' in actions))
                            resource_wild = (resources == '*' or (isinstance(resources, list) and '*' in resources))
                            if stmt.get('Effect') == 'Allow' and (action_wild or resource_wild):
                                logger.warning(f"Role {role_name} attached policy {ap['PolicyName']} is overly permissive for function {fn_name}.")
                                if not dry_run:
                                    try:
                                        iam_client.detach_role_policy(RoleName=role_name, PolicyArn=ap['PolicyArn'])
                                        logger.info(f"Detached policy {ap['PolicyName']} from role {role_name}.")
                                    except ClientError as e:
                                        logger.error(f"Failed to detach policy {ap['PolicyName']} from role {role_name}: {e}")
                                break
                except ClientError as e:
                    logger.error(f"Error inspecting role policies for {role_name}: {e}")

        # 4. Environment Variables Encryption
        if policy.get('environment_variables_encrypted', True):
            if not function.get('KmsKeyArn'):
                logger.warning(f"Lambda function {fn_name} does not have environment variables encrypted.")
                if not dry_run:
                    try:
                        kms_key_arn = policy.get('kms_key_arn')
                        if not kms_key_arn:
                            logger.warning("No kms_key_arn provided in policy for Lambda env encryption; skipping auto-remediation.")
                        else:
                            lambda_client.update_function_configuration(
                                FunctionName=fn_name,
                                KmsKeyArn=kms_key_arn
                            )
                            logger.info(f"Enabled environment variables encryption for Lambda function {fn_name} using {kms_key_arn}.")
                    except ClientError as e:
                        logger.error(f"Failed to set KMS key for {fn_name}: {e}")