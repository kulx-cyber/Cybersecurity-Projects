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


class RDSClient:
    def describe_db_instances(self):
        return {"DBInstances": []}

    def modify_db_instance(self, **kwargs):
        return {}


class MockSession:
    def client(self, name):
        assert name == 'rds'
        return RDSClient()


def test_rds_scanner_check_runs():
    from scanner.aws import rds_scanner
    rds_scanner.check(session=MockSession(), logger=DummyLogger(), dry_run=True, policy={})
