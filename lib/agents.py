from abc import ABCMeta, abstractmethod

from langroid import ChatAgent, ChatAgentConfig

from lib.utils import CodeGenSandbox
from TestRunner import GenericTestRunner


class GenericAgent(metaclass=ABCMeta):
    @abstractmethod
    def respond(self, prompt: str, *args, **kwargs) -> str: pass


class CodeGenAgent(GenericAgent):

    sandbox: CodeGenSandbox
    agent: ChatAgent
    class_skeleton: str
    previous_code_attempt: str
    latest_test_result: str
    latest_test_result_interpretation: str

    def __init__(self, sandbox: CodeGenSandbox, config: ChatAgentConfig):
        self.sandbox = sandbox

        with open(self.sandbox.get_sandboxed_class_path(), "r") as f:
            self.class_skeleton = f.read()

        self.agent = ChatAgent(config)

    def respond(self, prompt: str, *args, **kwargs) -> str:
        response = self.agent.llm_response(prompt)
        with open(self.sandbox.get_sandboxed_class_path(), "w+") as _out:
            _out.write(response.content)

        return response.content

    def set_previous_code_attempt(self, attempt: str) -> None:
        self.previous_code_attempt = attempt

    def set_latest_test_result(self, tr: str) -> None:
        self.latest_test_result = tr

    def set_latest_test_result_interpretation(self, interpretation: str) -> None:
        self.latest_test_result_interpretation = interpretation


class TestInterpreterAgent(GenericAgent):

    sandbox: CodeGenSandbox
    agent: ChatAgent
    latest_test_results: str
    latest_test_exit_code: int

    def __init__(self, sandbox: CodeGenSandbox, config: ChatAgentConfig) -> None:
        self.sandbox = sandbox
        self.agent = ChatAgent(config)

    def set_latest_test_results(self, results: str) -> None:
        self.latest_test_results = results

    def set_latest_test_exit_code(self, code: int) -> None:
        self.latest_test_exit_code = code

    def respond(self, prompt: str, *args, **kwargs) -> str:
        return self.agent.llm_response(prompt)
