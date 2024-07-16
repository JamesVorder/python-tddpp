import os
import typer

import langroid as lr
from langroid.utils.configuration import set_global, Settings
from langroid.utils.logging import setup_colored_logging

from TestRunner.GenericTestRunner import GenericTestRunner, InlineTestRunner, SubProcessTestRunner

app = typer.Typer()
setup_colored_logging()


def generate_first_attempt(class_skeleton: str) -> None:
    with open(class_skeleton, "r") as f:
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


def generate_next_attempt(test_results: str, test_results_insights: str) -> None:
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
            In addition, you may consider these insights about the test results when coming up with your solution:
            {test_results_insights}
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


def interpret_test_results(results: str) -> str:
    cfg = lr.ChatAgentConfig(
        llm=lr.language_models.OpenAIGPTConfig(
            chat_model="ollama/llama3:latest",
            chat_context_length=8000,
        ),
        vecdb=None
    )
    agent = lr.ChatAgent(cfg)
    prompt = f"""
        You are an expert at interpreting the results of unit tests, and providing insight into what they mean.
        You should be descriptive about what variables are incorrect, and in what way.
        You should include information about which methods should be modified, and in what way.
        You should generally not provide code.
        Please provide insights about the following test results:
        {results}
    """
    response = agent.llm_response(prompt)
    return response.content


def teardown() -> None:
    codegen_path = os.path.join(".", "generated")
    build_path = os.path.join(".", "build")
    if not os.path.exists(build_path):
        os.makedirs(build_path)
    with open(os.path.join(codegen_path, "test_class.py"), "r+") as generated_file:
        with open(os.path.join(build_path, "test_class.py"), "w+") as _out:
            _out.write(generated_file.read())
            generated_file.truncate(0)


def chat(class_skeleton: str, test_dir: str, test_runner: GenericTestRunner, max_epochs: int=5) -> None:
    generate_first_attempt(class_skeleton)
    solved = False
    for _ in range(max_epochs):
        # test_exit_code, test_results = get_test_results()
        test_exit_code, test_results = test_runner.run()
        print(test_results)
        if test_exit_code == 0:
            solved = True
            print("Done!")
            break
        elif test_exit_code == 1:
            results_insights = interpret_test_results(test_results)
            generate_next_attempt(test_results, results_insights)
        else:
            solved = True
            print("There is some problem with the test suite itself.")
            break
    teardown()
    if not solved:
        print(f"Reached the end of epoch {max_epochs} without finding a solution :(")

@app.command()
def main(
    debug: bool = typer.Option(False, "--debug", "-d", help="debug mode"),
    no_stream: bool = typer.Option(False, "--nostream", "-ns", help="no streaming"),
    nocache: bool = typer.Option(False, "--nocache", "-nc", help="don't use cache"),
    class_skeleton: str = typer.Option(None, "--class-skeleton", "-c", help="You must provide a class skeleton."),
    test_dir: str = typer.Option(os.path.join(".", "test"), "--test-dir", "-t", help=""),
) -> None:
    set_global(
        Settings(
            debug=debug,
            cache=not nocache,
            stream=not no_stream,
        )
    )
    assert os.path.isfile(class_skeleton), f"The class skeleton file provided does not exist! Got {class_skeleton}"
    assert os.path.exists(test_dir), f"The test-dir provided does not exist! Got {test_dir}"

    tr: GenericTestRunner = SubProcessTestRunner("", test_dir)
    chat(
        class_skeleton=class_skeleton,
        test_dir=test_dir,
        test_runner=tr
    )


if __name__ == "__main__":
    app()
