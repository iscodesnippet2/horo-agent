# Horo Agent

Horo Agent is a lightweight, independently maintained agent runtime based on the MIT-licensed [Hermes Agent](https://github.com/NousResearch/hermes-agent) project by Nous Research.

This repository is a downstream lite build focused on a smaller, enterprise-friendly install surface while keeping the core local agent experience usable through the `horo` CLI.

Horo Agent is not affiliated with, endorsed by, or sponsored by Nous Research.

## Current Status

This repo has been prepared as an independent downstream project:

- Package name: `horo-agent`
- Primary CLI command: `horo`
- Additional entrypoints: `horo-agent`, `horo-acp`
- Default home/config scope moved toward Horo paths
- Cloud checks removed from the lite doctor path
- Standalone config loading fixed for the downstream package
- Lite CLI startup and custom runtime fixes applied
- TTS streaming made optional for the lite CLI
- Local cron management, local cron execution, and memory CLI restored
- Platform labels shim added for the lite build
- Local code analysis artifacts ignored
- GitHub history was intentionally reset to a clean initial import to avoid pushing large upstream historical artifacts

The current public branch is `lite`.

## Purpose

Horo Agent is intended to be a practical downstream base for:

- Public PyPI packaging under an independent name
- Controlled internal adoption
- Air-gapped or controlled installation flows
- A reduced runtime surface compared with the full upstream Hermes Agent project
- Continued compatibility with selected Hermes Agent concepts, modules, and workflows

The project is not trying to be an official Hermes Agent release. It is a downstream implementation with its own packaging, release, and support boundary.

## Install

From PyPI or a package index, once published:

```bash
pip install horo-agent
horo
```

For local development from this checkout:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
horo --help
```

## Common Commands

```bash
horo              # Start the interactive CLI
horo --help       # Show CLI help
horo model        # Configure provider/model selection
horo tools        # Configure tools
horo config get   # Read config values
horo config set   # Set config values
horo doctor       # Diagnose local setup
horo-acp          # Start the ACP adapter entrypoint
```

## Lite Scope

Horo Agent keeps the local agent runtime as the center of gravity. The lite build currently favors:

- Local CLI usage
- Local configuration
- Local cron support
- Memory CLI support
- ACP/editor integration paths
- Reduced cloud/provider assumptions
- Explicit, pinned dependency management

Some full Hermes Agent surfaces, hosted services, docs, or installers may still exist in inherited code and documentation while the downstream cleanup continues. Treat upstream references as provenance or compatibility context unless this README explicitly marks them as Horo-supported.

## Repository History

This repository was imported from the current downstream `lite` state as a clean initial Git history. That choice was intentional:

- The upstream history contained large historical artifacts.
- Full-history pushes were unreliable and unnecessarily heavy for the downstream repo.
- A clean import gives Horo Agent a smaller public repository for packaging and downstream maintenance.

Upstream attribution is preserved in this README and in the MIT license notices.

## Upstream

Horo Agent is derived from:

- Project: Hermes Agent
- Upstream repository: https://github.com/NousResearch/hermes-agent
- Upstream license: MIT

The original upstream copyright notice is preserved in `LICENSE`.

## Security And Dependency Review

This project uses pinned dependencies in `pyproject.toml` and `uv.lock`. GitHub Dependabot may report vulnerabilities when a pinned direct or transitive dependency matches a known advisory.

## Development Notes

Useful checks:

```bash
python -m build
pip install dist/*.whl
horo --help
python -m pytest
```

If you are preparing a release, verify in a fresh virtual environment before publishing:

```bash
python -m venv /tmp/horo-agent-smoke
source /tmp/horo-agent-smoke/bin/activate
pip install dist/*.whl
horo --help
horo-agent --help
horo-acp --help
```

## License

MIT. See [LICENSE](LICENSE).

This project includes code derived from the MIT-licensed Hermes Agent project by Nous Research. Horo Agent is independently maintained and is not affiliated with, endorsed by, or sponsored by Nous Research.
