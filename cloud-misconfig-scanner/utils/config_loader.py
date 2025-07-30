import yaml
import os

def load_policy(policy_path, cli_dry_run=False):
    if not os.path.exists(policy_path):
        raise FileNotFoundError(f"Policy file not found: {policy_path}")

    with open(policy_path, 'r') as f:
        config = yaml.safe_load(f)

    # Inject CLI --dry-run if present
    if cli_dry_run:
        config.setdefault('global', {})['dry_run'] = True

    # Ensure essential fields exist
    if 'global' not in config:
        raise KeyError("Missing 'global' section in policy.")
    if 'services' not in config or not isinstance(config['services'], dict):
        raise KeyError("Missing or invalid 'services' section in policy.")

    return config
