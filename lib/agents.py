from abc import ABCMeta, abstractmethod

from langroid import ChatAgent, ChatAgentConfig

from lib.utils import CodeGenSandbox


class GenericAgent(metaclass=ABCMeta):
    @abstractmethod
    def respond(self, prompt: str, *args, **kwargs) -> str: pass


class FirstAttemptAgent(GenericAgent):

    def __init__(self, sandbox: CodeGenSandbox, config: ChatAgentConfig):
        self.sandbox = sandbox

        with open(self.sandbox.get_sandboxed_class_path(), "r") as f:
            self.class_skeleton = f.read()

        self.agent = ChatAgent(config)

    def respond(self, prompt: str, *args, **kwargs) -> str:
        response = self.agent.llm_response()
        with open(self.sandbox.get_sandboxed_class_path(), "w+") as _out:
            _out.write(response.content)

        return response.content
