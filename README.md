# TDD++

The goal of this tool is to bring TDD to the next level.
Rather than writing tests first, let's write tests _only_.
Provided is a command line tool, which, given a class skeleton and a test suite,
will generate successive class implementations until all tests pass.

This work is heavily based off of the work in [Mohannadcse/AlloySpecRepair](https://github.com/Mohannadcse/AlloySpecRepair).

## Dependencies
* `ollama`
* `llama3:latest`
* `poetry`

### Serving Your Own LLM
In order to run the code as-is, you must self serve your own LLM locally.
Currently, this is hard-coded to llama3:latest.
If you have ollama installed, self serving this LLM locally is trivial:

```commandline
ollama serve
ollama run llama3:latest
```

## Running The Tool
For usage information, run:
```commandline
poetry run python -m main --help
```

# Roadmap
* Containerization
* Configurable OpenAI API key for ChatGPT usage
