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


class SSMClient:
    def list_documents(self):
        return {"DocumentIdentifiers": []}

    def get_document(self, Name):
        # Minimal structure to satisfy ssm_scanner usage
        return {"Name": Name}

    def list_compliance_summaries(self):
        return {"ComplianceSummaryItems": []}


class MockSession:
    def client(self, name):
        assert name == 'ssm'
        return SSMClient()


def test_ssm_scanner_check_runs():
    from scanner.aws import ssm_scanner
    ssm_scanner.check(session=MockSession(), logger=DummyLogger(), dry_run=True, policy={})
