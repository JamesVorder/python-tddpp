from abc import ABCMeta, abstractmethod

import pytest

from pytest_plugins import ResultsCollector, SessionStartPlugin


class GenericTestRunner(metaclass=ABCMeta):
    @abstractmethod
    def run(self, *args, **kwargs) -> (int, str): pass

import subprocess


class SubProcessTestRunner(GenericTestRunner):
    code_dir: str
    test_dir: str

    def __init__(self, _code, _test) -> None:
        self.code_dir = _code
        self.test_dir = _test

    def run(self, *args, **kwargs) -> (int, str):
        # TODO: check that code_dir and test_dir exist
        proc = subprocess.run(["pytest", self.test_dir], capture_output=True)
        return proc.returncode, proc.stdout


class InlineTestRunner(GenericTestRunner):

    def __init__(self, _code, _test) -> None:
        self.code_dir = _code
        self.test_dir = _test

    def run(self, *args, **kwargs) -> (int, str):
        collector = ResultsCollector()
        setup = SessionStartPlugin()
        pytest.main(args=["-k", "ExampleClass"], plugins=[collector, setup])
        _out = ""

        if collector.exitcode > 0:
            for report in collector.reports:
                _out += f"{report.outcome.upper()} {report.nodeid} ... Outcome: - {report.longrepr.reprcrash.message}"
                _out += "\n"
                _out += report.longreprtext
                _out += "\n"
        return collector.exitcode, _out
