import pytest
import time
try:
    import generated.test_class
except ImportError:
    pass  # Since this is a generated file, it sometimes doesn't exist.


class ResultsCollector:
    def __init__(self):
        self.reports = []
        self.collected = 0
        self.exitcode = 0
        self.passed = 0
        self.failed = 0
        self.xfailed = 0
        self.skipped = 0
        self.total_duration = 0

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        report = outcome.get_result()
        if report.when == 'call':
            self.reports.append(report)

    def pytest_collection_modifyitems(self, items):
        self.collected = len(items)

    def pytest_terminal_summary(self, terminalreporter, exitstatus):
        self.exitcode = exitstatus
        self.passed = len(terminalreporter.stats.get('passed', []))
        self.failed = len(terminalreporter.stats.get('failed', []))
        self.xfailed = len(terminalreporter.stats.get('xfailed', []))
        self.skipped = len(terminalreporter.stats.get('skipped', []))

        self.total_duration = time.time() - terminalreporter._sessionstarttime


class SessionStartPlugin:
    """
    The goal of this plugin is to allow us to run pytest multiple times
    and have it pick up the changes we generate in `generated/test_class.py`
    """
    def pytest_sessionstart(self):
        if globals().get('generated', None) is not None:
            import importlib
            print("Reloading generated.test_class module...")
            importlib.reload(generated.test_class)