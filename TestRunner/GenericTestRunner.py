import subprocess
from lib.utils import CodeGenSandbox
from abc import ABCMeta, abstractmethod


class GenericTestRunner(metaclass=ABCMeta):
    @abstractmethod
    def run(self, *args, **kwargs) -> (int, str): pass


class SubProcessTestRunner(GenericTestRunner):

    sandbox: CodeGenSandbox

    def __init__(self, sandbox: CodeGenSandbox) -> None:
        self.sandbox = sandbox

    def run(self, *args, **kwargs) -> (int, str):
        proc = subprocess.run(
            ["pytest", self.sandbox.test_path],
            cwd=self.sandbox.get_sandboxed_project_path(),
            capture_output=True,
            universal_newlines=True
        )
        return proc.returncode, proc.stdout


# TODO: This implementation is currently defunct
# class InlineTestRunner(GenericTestRunner):
#
#     def __init__(self, sandbox) -> None:
#         self.test_dir = sandbox.get_sandboxed_test_path()
#
#     def run(self, *args, **kwargs) -> (int, str):
#         collector = ResultsCollector()
#         setup = SessionStartPlugin()
#         # TODO: Remove the ExampleClass reference here.
#         pytest.main(args=["-k", "ExampleClass"], plugins=[collector, setup])
#         _out = ""
#
#         if collector.exitcode > 0:
#             for report in collector.reports:
#                 _out += f"{report.outcome.upper()} {report.nodeid} ... Outcome: - {report.longrepr.reprcrash.message}"
#                 _out += "\n"
#                 _out += report.longreprtext
#                 _out += "\n"
#         return collector.exitcode, _out
