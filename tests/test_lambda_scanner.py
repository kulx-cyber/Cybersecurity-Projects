import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))


class DummyLogger:
    def info(self, *args, **kwargs):
        pass
    def warning(self, *args, **kwargs):
        pass
    def error(self, *args, **kwargs):
        pass


class IAMClient:
    def list_attached_role_policies(self, RoleName):
        return {"AttachedPolicies": []}
    def get_policy(self, PolicyArn):
        return {"Policy": {"DefaultVersionId": "v1"}}
    def get_policy_version(self, PolicyArn, VersionId):
        return {"PolicyVersion": {"Document": {"Statement": []}}}


class LambdaClient:
    def list_functions(self):
        return {"Functions": [{"FunctionName": "fn1", "Timeout": 70, "TracingConfig": {"Mode": "PassThrough"}, "Role": "arn:aws:iam::123456789012:role/r", "KmsKeyArn": None}]}
    def update_function_configuration(self, FunctionName, **kwargs):
        return {}


class MockSession:
    def client(self, name):
        if name == 'lambda':
            return LambdaClient()
        if name == 'iam':
            return IAMClient()
        raise AssertionError(name)


def test_lambda_scanner_check_runs():
    from scanner.aws import lambda_scanner
    lambda_scanner.check(session=MockSession(), logger=DummyLogger(), dry_run=True, policy={})
