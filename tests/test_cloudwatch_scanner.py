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


class CloudWatchClient:
    def describe_alarms(self):
        return {"MetricAlarms": []}


class MockSession:
    def client(self, name):
        assert name == 'cloudwatch'
        return CloudWatchClient()


def test_cloudwatch_scanner_check_runs():
    from scanner.aws import cloudwatch_scanner
    cloudwatch_scanner.check(session=MockSession(), logger=DummyLogger(), dry_run=True, policy={"alarm_on_root_login": True, "alarm_on_suspicious_api_calls": True, "alarm_on_unauthorized_api_calls": True})
