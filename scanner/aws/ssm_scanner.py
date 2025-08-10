import boto3
from botocore.exceptions import ClientError

def check(session, logger, dry_run, policy):
    ssm_client = session.client("ssm")
    logger.info("Starting SSM checks...")

    if policy.get("document_permissions", True):
        docs = ssm_client.list_documents()["DocumentIdentifiers"]
        for doc in docs:
            perms = ssm_client.describe_document_permission(Name=doc["Name"], PermissionType="Share")
            if any(p == "All" for p in perms.get("AccountIds", [])):
                logger.warning(f"Document {doc['Name']} is shared publicly.")

    if policy.get("session_logging", True):
        logs = ssm_client.get_document(Name="SSM-SessionManagerRunShell")
        if "CloudWatch" not in str(logs):
            logger.warning("SSM session logging not properly configured.")

    if policy.get("patch_compliance", True):
        compliance = ssm_client.list_compliance_summaries()["ComplianceSummaryItems"]
        if not compliance:
            logger.warning("No patch compliance info found.")

