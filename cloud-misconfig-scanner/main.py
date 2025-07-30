import argparse
import sys

from utils.config_loader import load_policy
from utils.logger import setup_logger
from core.runner import run_checks

def get_user_services(available_services):
    print("Available Services to Run:")
    for i, service in enumerate(available_services, start=1):
        print(f"{i}. {service}")

    selected_services = input("Enter the numbers of the services to run (comma-separated): ")
    try:
        indexes = [int(i.strip()) -1 for i in selected_services.split(',')]
        selected_services = [available_services[i] for i in indexes if 0 <= i < len(available_services)]
        if not selected_services:
            raise ValueError("No valid services selected.")
        return selected_services
    except ValueError:
        print("Invalid input. Please enter numbers only.")
        sys.exit(1)

def display_banner():
    print("""
    ############################################################
    #                                                          #
    #   Cloud Misconfiguration Scanner                         #
    #   Version: 1.0                                           #
    #                                                          #
    ############################################################
    """)

def parse_args():
    parser = argparse.ArgumentParser(description="Cloud Misconfiguration Scanner CLI", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode to input AWS credentials')
    parser.add_argument('--cloud', type=str, default='aws', help='Cloud provider to scan (e.g., aws, azure, gcp)')
    parser.add_argument('--dry-run', action='store_true', help='Run the scanner without making any changes')
    parser.add_argument('--policy', type=str, default='./config/policy.yaml', help='Path to Policy YAML file')
    parser.add_argument('--log', type=str, default='./logs/cloud_scanner.log', help='Path to log file')
    parser.add_argument('--log-level', type=str, default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Set the logging level')
    args = parser.parse_args()
    return args

def main():
    args = parse_args()

    #setup logger
    logger = setup_logger(log_level=args.log_level, log_file=args.log)
    logger.info("Starting cloud misconfiguration scanner...")

    # Display Header
    display_banner()

    # Load policy
    try:
        config = load_policy(args.policy, cli_dry_run=args.dry_run)
        logger.info(f"Loaded policy from {args.policy}")
    except Exception as e:
        logger.error(f"Failed to load policy: {e}")
        sys.exit(1)

    available_services = list(config.get("services", {}).keys())

    if not available_services:
        logger.warning("No available services found in policy.yaml.")
        sys.exit(1)

    #User input for services
    services_to_run = get_user_services(available_services)

    logger.info(f"Selected services to run: {', '.join(services_to_run)}")
    logger.info(f"Dry run mode: {'Enabled' if args.dry_run else 'Disabled'}")

    # Run checks
    try:
        run_checks(
            interactive=args.interactive,
            cloud=args.cloud,
            services=services_to_run,
            dry_run=args.dry_run,
            logger=logger,
            policy=config
        )
        logger.info("Cloud misconfiguration scan completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred during the scan: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()