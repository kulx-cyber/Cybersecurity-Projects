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
    def describe_security_groups(self):
        return {"SecurityGroups": []}
    def describe_instances(self):
        return {"Reservations": []}
    def describe_volumes(self):
        return {"Volumes": []}


class MockSession:
    def client(self, name):
        assert name == 'ec2'
        return EC2Client()


def test_ec2_scanner_check_runs():
    from scanner.aws import ec2_scanner
    ec2_scanner.check(session=MockSession(), logger=DummyLogger(), dry_run=True, policy={})
