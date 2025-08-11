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


class SQSClient:
    def list_queues(self):
        return {"QueueUrls": []}


class MockSession:
    def client(self, name):
        assert name == 'sqs'
        return SQSClient()


def test_sqs_scanner_check_runs():
    from scanner.aws import sqs_scanner
    sqs_scanner.check(session=MockSession(), logger=DummyLogger(), dry_run=True, policy={})
