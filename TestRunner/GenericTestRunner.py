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
