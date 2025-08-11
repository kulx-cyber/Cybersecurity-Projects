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


class SNSClient:
    def list_topics(self):
        return {"Topics": []}


class MockSession:
    def client(self, name):
        assert name == 'sns'
        return SNSClient()


def test_sns_scanner_check_runs():
    from scanner.aws import sns_scanner
    sns_scanner.check(session=MockSession(), logger=DummyLogger(), dry_run=True, policy={})
