import boto3
from botocore.exceptions import ClientError

def check(session, logger, dry_run, policy):
    elb_client = session.client("elbv2")
    logger.info("Starting ELB checks...")

    lbs = elb_client.describe_load_balancers().get('LoadBalancers', [])
    for lb in lbs:
        lb_name = lb.get('LoadBalancerName')
        logger.info(f"Checking Load Balancer: {lb_name}")

        # 1. Check for Deletion protection
        if policy.get("deletion_protection", True):
            attrs = elb_client.describe_load_balancer_attributes(
                LoadBalancerArn=lb.get('LoadBalancerArn')
            )
            if not any(attr['Value'] == 'true' for attr in attrs['Attributes'] if attr['Key'] == 'deletion_protection.enabled'):
                logger.warning(f"Load Balancer {lb_name} does not have deletion protection enabled.")
                if not dry_run:
                    elb_client.modify_load_balancer_attributes(
                        LoadBalancerArn=lb.get('LoadBalancerArn'),
                        Attributes=[
                            {
                                'Key': 'deletion_protection.enabled',
                                'Value': 'true'
                            },
                        ]
                    )
                    logger.info(f"Enabled deletion protection for Load Balancer {lb_name}.")

        # 2. Check for Idle timeout
        if policy.get("idle_timeout", True):
            timeout = next((attr['Value'] for attr in attrs['Attributes'] if attr['Key'] == 'idle_timeout.timeout_seconds'), None)
            # timeout is already the string value; convert and compare
            if timeout is not None and int(timeout) < 60:
                logger.warning(f"Load Balancer {lb_name} has an idle timeout of {timeout} seconds, which is less than the recommended 60 seconds.")
                if not dry_run:
                    elb_client.modify_load_balancer_attributes(
                        LoadBalancerArn=lb.get('LoadBalancerArn'),
                        Attributes=[
                            {
                                'Key': 'idle_timeout.timeout_seconds',
                                'Value': '60'
                            },
                        ]
                    )
                    logger.info(f"Updated idle timeout for Load Balancer {lb_name} to 60 seconds.")

        # 3. Check for ssl policies on listeners
        if policy.get("ssl_policies", True):
            listeners = elb_client.describe_listeners(
                LoadBalancerArn=lb.get('LoadBalancerArn')
            ).get('Listeners', [])
            for listener in listeners:
                if listener.get('Protocol') == 'HTTPS' and 'SslPolicy' in listener:
                    if not listener['SslPolicy'].startswith('ELBSecurityPolicy'):
                        logger.warning(f"Load Balancer {lb_name} has a weak SSL policy: {listener['SslPolicy']}.")
                        if not dry_run:
                            elb_client.modify_listener(
                                ListenerArn=listener['ListenerArn'],
                                SslPolicy='ELBSecurityPolicy-2016-08',
                            )
                            logger.info(f"Updated SSL policy for Load Balancer {lb_name}.")

        # 4. Check for access logs
        if policy.get("access_logs", True):
            attrs = elb_client.describe_load_balancer_attributes(
                LoadBalancerArn=lb.get('LoadBalancerArn')
            )
            if not any(attr['Value'] == 'true' for attr in attrs['Attributes'] if attr['Key'] == 'access_logs.s3.enabled'):
                logger.warning(f"Load Balancer {lb_name} does not have access logs enabled.")
                if not dry_run:
                    elb_client.modify_load_balancer_attributes(
                        LoadBalancerArn=lb.get('LoadBalancerArn'),
                        Attributes=[
                            {
                                'Key': 'access_logs.s3.enabled',
                                'Value': 'true'
                            },
                        ]
                    )
                    logger.info(f"Enabled access logs for Load Balancer {lb_name}.")
