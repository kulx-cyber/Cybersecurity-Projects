import boto3
from botocore.exceptions import ClientError

REQUIRED_METRICS = {
    "alarm_on_root_login": {
        "MetricName": "RootAccountUsage",
        "Namespace": "CloudTrailMetrics",
    },
    "alarm_on_suspicious_api_calls": {
        "MetricName": "SuspectedMaliciousActivity",
        "Namespace": "CloudTrailMetrics",
    },
    "alarm_on_unauthorized_api_calls": {
        "MetricName": "UnauthorizedAPICalls",
        "Namespace": "CloudTrailMetrics",
    }
}

def check(session, logger, dry_run, policy):
    cloudwatch_client = session.client("cloudwatch")
    logger.info("Starting CloudWatch policy checks...")

    try:
        alarms = cloudwatch_client.describe_alarms().get('MetricAlarms', [])
        logger.info(f"Found {len(alarms)} CloudWatch alarms.")
    except ClientError as e:
        logger.error(f"Error listing CloudWatch alarms: {e}")
        return
    
    for check_name, metric_info in REQUIRED_METRICS.items():
        if policy.get(check_name, True):
            found = False
            logger.info(f"Checking for CloudWatch alarm: {check_name}")
            # Check if the alarm already exists
            for alarm in alarms:
                if(alarm.get("MetricName") == metric_info["MetricName"] and
                     alarm.get("Namespace") == metric_info["Namespace"]):
                      found = True
                      logger.warning(f"CloudWatch alarm {alarm['AlarmName']} is already configured for {check_name}.")
                      break

            if not found:
                logger.warning(f"Creating CloudWatch alarm for {check_name}.")
                
                if not dry_run:
                    cloudwatch_client.put_metric_alarm(
                        AlarmName=f"{check_name}_alarm",
                        MetricName=metric_info["MetricName"],
                        Namespace=metric_info["Namespace"],
                        Statistic='Sum',
                        Period=300,
                        EvaluationPeriods=1,
                        Threshold=1,
                        ComparisonOperator='GreaterThanOrEqualToThreshold',
                        ActionsEnabled=True,
                        AlarmActions=['arn:aws:sns:us-east-1:123456789012:MySNSTopic'],
                        AlarmDescription=f"Alarm for {check_name}",
                    )
                logger.info(f"Created CloudWatch alarm for {check_name}.")