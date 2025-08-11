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
    def list_users(self):
        return {"Users": []}


class MockSession:
    def client(self, name):
        assert name == 'iam'
        return IAMClient()


def test_iam_scanner_check_runs(monkeypatch):
    from scanner.aws import iam_scanner
    iam_scanner.check(session=MockSession(), logger=DummyLogger(), dry_run=True, policy={})
