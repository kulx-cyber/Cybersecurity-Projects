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


class EC2Client:
    def describe_volumes(self):
        return {"Volumes": []}
    def describe_snapshots(self, OwnerIds=None):
        return {"Snapshots": []}


class MockSession:
    def client(self, name):
        assert name == 'ec2'
        return EC2Client()


def test_ebs_scanner_check_runs():
    from scanner.aws import ebs_scanner
    ebs_scanner.check(session=MockSession(), logger=DummyLogger(), dry_run=True, policy={})
