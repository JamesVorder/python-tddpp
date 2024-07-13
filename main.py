import os
import typer

# for the test runner
import pytest
# ------------------

import langroid as lr
from langroid.utils.configuration import set_global, Settings
from langroid.utils.logging import setup_colored_logging

from pytest_plugins import ResultsCollector, SessionStartPlugin

app = typer.Typer()
setup_colored_logging()


def generate_first_attempt() -> None:
    # code_prompt = typer.Prompt("Describe what kind of code you want.")
    # class_skeleton: str = ""
    with open(os.path.join(".", "assets", "test_class.py"), "r") as f:
        class_skeleton = f.read()

    cfg = lr.ChatAgentConfig(
        llm=lr.language_models.OpenAIGPTConfig(
            chat_model="ollama/llama3:latest",
            chat_context_length=8000,
        ),
        vecdb=None
    )
    main_agent = lr.ChatAgent(cfg)
    response = main_agent.llm_response(f"You are an expert at writing Python code."
                                       f"Fill in the following class skeleton."
                                       f"Do NOT add any other methods or commentary."
                                       f"Your response should be ONLY the python code."
                                       f"Do not say 'here is the python code'"
                                       f"Your output MUST be valid, runnable python code and NOTHING else."
                                       f"{class_skeleton}")
    with open(os.path.join(".", "generated", "test_class.py"), "w+") as _out:
        _out.write(response.content)


def get_test_results() -> str:
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


def generate_next_attempt(test_results: str) -> None:
    cfg = lr.ChatAgentConfig(
        llm=lr.language_models.OpenAIGPTConfig(
            chat_model="ollama/llama3:latest",
            chat_context_length=8000,
        ),
        vecdb=None
    )
    agent = lr.ChatAgent(cfg)
    with open(os.path.join(".", "generated", "test_class.py"), "r") as f:
        code_snippet = f.read()

    prompt = f"""
            You are an expert at writing Python code.
            Consider the following code, and test results.
            Here is the code:
            {code_snippet}
            Here are the test results:
            {test_results}
            Update the code so that the tests will pass.
            Your output MUST contain all the same classes and methods as the input code.
            Do NOT add any other methods or commentary.
            Your response should be ONLY the python code.
            Do not say 'here is the python code'
            Do not surround your response with quotes or backticks.
            Your output MUST be valid, runnable python code and NOTHING else.
        """
    response = agent.llm_response(prompt)
    with open(os.path.join(".", "generated", "test_class.py"), "w") as _out:
        _out.write(response.content)


def chat() -> None:
    generate_first_attempt()
    for _ in range(5):
        test_exit_code, test_results = get_test_results()
        if test_exit_code == 1:
            generate_next_attempt(test_results)
        else:
            break
    print("Done! All tests are passing, or there is some problem with the test suite itself.")

@app.command()
def main(
    debug: bool = typer.Option(False, "--debug", "-d", help="debug mode"),
    no_stream: bool = typer.Option(False, "--nostream", "-ns", help="no streaming"),
    nocache: bool = typer.Option(False, "--nocache", "-nc", help="don't use cache"),
) -> None:
    set_global(
        Settings(
            debug=debug,
            cache=not nocache,
            stream=not no_stream,
        )
    )
    chat()


if __name__ == "__main__":
    app()
