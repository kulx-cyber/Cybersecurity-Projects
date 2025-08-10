import boto3
import getpass
import logging

def get_aws_session(interactive: bool = False):
    # Create a session with AWS credentials
    if interactive:
        # Prompt for AWS credentials if running interactively
        aws_access_key_id = input("Enter your AWS Access Key ID: ").strip()
        aws_secret_access_key = getpass.getpass("Enter your AWS Secret Access Key: ").strip()
        aws_region = input("Enter your AWS Region (default: us-east-1): ").strip() or "us-east-1"

        if aws_access_key_id and aws_secret_access_key:
            # Create a session with the provided credentials
            session = boto3.Session(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=aws_region
        )
        else:
            # Use default credentials from the environment or config file
            session = boto3.Session(region_name="us-east-1")
    else:
        # Use default credentials from the environment or config file
        session = boto3.Session(region_name="us-east-1")

    return session
