import os

from langroid import ChatAgentConfig

from lib.utils import CodeGenSandbox
from lib.agents import CodeGenAgent, TestInterpreterAgent, GenericAgent
import typer

import langroid as lr
from langroid.utils.configuration import set_global, Settings
from langroid.utils.logging import setup_colored_logging

from TestRunner.GenericTestRunner import GenericTestRunner, SubProcessTestRunner

app = typer.Typer()
setup_colored_logging()


def chat(
        code_gen_agent: GenericAgent,
        test_interpreter: GenericAgent,
        test_runner: GenericTestRunner,
        max_epochs: int = 5
) -> None:
    code_attempt = code_gen_agent.respond(
        prompt=f"""
            You are an expert at writing Python code.
            Fill in the following class skeleton.
            Do NOT add any other methods or commentary.
            Your response should be ONLY the python code.
            Do not say 'here is the python code'
            Do not surround your response with quotes or backticks.
            DO NOT EVER USE ``` in your output.
            You should maintain any comments that were provided in the class skeleton.
            You should maintain the exact method signatures provided in the class skeleton.
            Your output MUST be valid, runnable python code and NOTHING else.
            Your output MUST NOT include any usage of testing tools like unittest, pytest, mock, etc.
            {code_gen_agent.class_skeleton}
        """
    )
    solved = False
    for _ in range(max_epochs - 1):
        # test_exit_code, test_result(s = get_test_results()
        test_exit_code, test_results = test_runner.run()
        print(test_results)
        if test_exit_code == 0:
            solved = True
            print("Done!")
            break
        else:
            test_interpreter.set_latest_test_results(test_results)
            test_interpreter.set_latest_test_exit_code(test_exit_code)
            results_insights = test_interpreter.respond(
                prompt=f"""
                You are an expert at interpreting the results of unit tests, and providing insight into what they mean.
                You should be descriptive about what variables are incorrect, and in what way.
                You should include information about which methods should be modified, and in what way (without providing code.)
                You should not provide code.
                You should NEVER attempt to modify the tests, or give advice to modify the tests.
                Give results in a bulleted list, with one bullet for each method that fails tests.
                Keep insights very brief, providing a maximum of 3 sentences about each method that failed a test.
                Please provide insights about the following test results:
                {test_interpreter.latest_test_results}
                Those results were produced by the following code:
                {test_interpreter.latest_test_exit_code}
                """
            )
            code_gen_agent.set_previous_code_attempt(code_attempt)
            code_gen_agent.set_latest_test_result(test_results)
            code_gen_agent.set_latest_test_result_interpretation(results_insights)
            code_attempt = code_gen_agent.respond(
                prompt=f"""
                You are an expert at writing Python code.
                Consider the following code, and the following test results.
                Here is the code:
                {code_gen_agent.previous_code_attempt}
                Here are the test results:
                {code_gen_agent.latest_test_result}
                In addition, you may consider these insights about the test results when coming up with your solution:
                {code_gen_agent.latest_test_result_interpretation}
                Update the code so that the tests will pass.
                Your output MUST contain all the same classes and methods as the input code.
                Do NOT add any other methods or commentary.
                Your response should be ONLY the python code.
                Do not say 'here is the python code'
                Do not surround your response with quotes or backticks.
                DO NOT EVER USE ``` in your output.
                Your response should NEVER start or end with ```
                You should maintain any comments that were provided in the code.
                You should maintain the exact method signatures provided in the code.
                Your output MUST be valid, runnable python code and NOTHING else.
                Your output MUST NOT include any usage of testing tools like unittest, pytest, mock, etc.
                """
            )
    if not solved:
        print(f"Reached the end of epoch {max_epochs} without finding a solution :(")


@app.command()
def main(
    debug: bool = typer.Option(False, "--debug", "-d", help="debug mode"),
    no_stream: bool = typer.Option(False, "--nostream", "-ns", help="no streaming"),
    nocache: bool = typer.Option(False, "--nocache", "-nc", help="don't use cache"),
    project_dir: str = typer.Argument(
        default=".",
        help="The project directory that contains your tests and class skeleton. "
             "This directory may also have other contents. "
             "The directory you give here will be cloned into a 'sandbox' for the code generator to operate in."
    ),
    class_skeleton_path: str = typer.Argument(
        default=os.path.join("assets", "test_class.py"),
        help="Path to the class skeleton file, relative to project_dir."
    ),
    test_path: str = typer.Argument(
        default=os.path.join(".", "test"),
        help="Path to the test file or directory, relative to project_dir."
    ),
    sandbox_path: str = typer.Option(
        "./build", "--sandbox-path", "-s",
        help="You may optionally specify a location for the sandbox in which the code generator operates."
             "Default: ./build"
    ),
    max_epochs: int = typer.Option(
        5, "--max-epochs", "-n", help="The maximum number of times to let the code generator try"
                                      "before giving up."
    )
) -> None:
    set_global(
        Settings(
            debug=debug,
            cache=not nocache,
            stream=not no_stream,
        )
    )

    llama3 = ChatAgentConfig(
        llm=lr.language_models.OpenAIGPTConfig(
            chat_model="ollama/llama3.1:latest",
            chat_context_length=128000
        ),
        vecdb=None
    )

    sandbox = CodeGenSandbox(project_dir, class_skeleton_path, test_path, sandbox_path)
    sandbox.init_sandbox()
    code_generator: GenericAgent = CodeGenAgent(sandbox, llama3)
    test_interpreter: GenericAgent = TestInterpreterAgent(sandbox, llama3)
    test_runner: GenericTestRunner = SubProcessTestRunner(sandbox)
    chat(code_generator, test_interpreter, test_runner, max_epochs)


if __name__ == "__main__":
    app()
