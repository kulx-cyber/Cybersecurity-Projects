import importlib
import enum
from scanner.aws import s3_scanner 
from scanner.aws import iam_scanner
from scanner.aws import ec2_scanner
from scanner.aws import rds_scanner
from scanner.aws import cloudtrail_scanner
from scanner.aws import cloudwatch_scanner
from utils.aws_session import get_aws_session

class ProcessType(enum.Enum):
    SCAN = 1
    REMEDIATE = 2

def run_process(interactive, cloud, services, dry_run, logger, policy, process):
    logger.info(f"Running {'checks' if process == ProcessType.SCAN else 'remediation'} for cloud provider: {cloud}")
    logger.info(f"Services to check: {', '.join(services)}")
    logger.info(f"Dry run mode: {'Enabled' if dry_run else 'Disabled'}")

    session = get_aws_session(interactive=interactive)

    # Check logic
    for service in services:
        logger.info(f"{'Checking' if process == ProcessType.SCAN else 'Remediating'} service: {service}")
        # Simulate a check
        try:
            # Dynamic import of service module
            if process == ProcessType.SCAN:
                module_path = f"scanner.{cloud}.{service.lower()}_scanner"
                service_module = importlib.import_module(module_path)

                service_module.check(
                    session=session,
                    logger=logger,
                    dry_run=dry_run,
                    policy=policy.get("services", {}).get(service, {})
                )
            else:
                module_path = f"remediator.{cloud}.{service.lower()}_remediator"
                service_module = importlib.import_module(module_path)

                service_module.remediate(
                    session=session,
                    logger=logger,
                    dry_run=dry_run,
                    policy=policy.get("services", {}).get(service, {})
                )
        except ModuleNotFoundError:
            logger.error(f"Service module not found: {module_path}. Please ensure it exists.")
        except AttributeError:
            logger.error(f"Service {service} does not have a {'check' if process == ProcessType.SCAN else 'remediate'} function. Please implement it.")
        except Exception as e:
            logger.error(f"Error checking service {service}: {e}")

    logger.info(f"All {'checks' if process == ProcessType.SCAN else 'remediation'} completed.")