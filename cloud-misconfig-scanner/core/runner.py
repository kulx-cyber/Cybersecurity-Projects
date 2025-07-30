import importlib
from scanner.aws import s3_scanner
from utils.aws_session import get_aws_session

def run_checks(interactive, cloud, services, dry_run, logger, policy):
    logger.info(f"Running checks for cloud provider: {cloud}")
    logger.info(f"Services to check: {', '.join(services)}")
    logger.info(f"Dry run mode: {'Enabled' if dry_run else 'Disabled'}")

    session = get_aws_session(interactive=interactive)

    # Placeholder for actual check logic
    for service in services:
        logger.info(f"Checking service: {service}")
        # Simulate a check
        try:
            # Dynamic import of service module
            module_path = f"scanner.{cloud}.{service.lower()}_scanner"
            service_module = importlib.import_module(module_path)

            service_module.check(
                session=session,
                logger=logger,
                dry_run=dry_run,
                policy=policy.get("services", {}).get(service, {})
            )
        except ModuleNotFoundError:
            logger.error(f"Service module not found: {module_path}. Please ensure it exists.")
        except AttributeError:
            logger.error(f"Service {service} does not have a 'check' function. Please implement it.")
        except Exception as e:
            logger.error(f"Error checking service {service}: {e}")

    logger.info("All checks completed.")