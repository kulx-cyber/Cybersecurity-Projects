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


class ELBv2Client:
    def describe_load_balancers(self):
        return {"LoadBalancers": []}


class MockSession:
    def client(self, name):
        assert name == 'elbv2'
        return ELBv2Client()


def test_elb_scanner_check_runs():
    from scanner.aws import elb_scanner
    elb_scanner.check(session=MockSession(), logger=DummyLogger(), dry_run=True, policy={})
