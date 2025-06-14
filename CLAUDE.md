# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Environment

This project uses devenv (Nix) for reproducible development environments:
- `devenv shell` - Enter the development environment
- `devenv up` - Start services (if any)
- `devenv test` - Run tests via devenv

## Python Environment & Dependencies

Uses uv for Python package management:
- `uv sync` - Install/sync dependencies from uv.lock
- `uv add <package>` - Add new dependency

## Code Quality & Formatting

Configured with pre-commit hooks via devenv:
- `ruff format .` - Format all Python code
- `ruff check --fix .` - Lint and auto-fix Python code
- Pre-commit hooks automatically run ruff on git commits

## Application Commands

The main CLI entry point is through the `release` module:
- `release --help` - Show available commands
- `release -f release.yaml start` - Start release process
- `release -f release.yaml validate` - Validate config file
- `release.tui` - Launch TUI application (experimental)

## Architecture Overview

### Core Components

Components located in the `release` package:
- **CLI Layer** (`cli.py`) - Click-based command interface with `start` and `validate` commands
- **Configuration** (`config.py`) - Pydantic models for release.yaml parsing and validation
- **Step Execution** (`steps.py`) - Core step runner that orchestrates git and runner actions
- **TUI Application** (`tui.py`) - Textual-based terminal user interface
- **Variable Parsing** (`parser.py`) - Template rendering with environment variables

### Action Modules

- **Git Module** (`git/`) - Git operations including shortlog generation
- **Runner Module** (`runner/`) - Command/script execution with environment setup

### Configuration Structure

Release processes are defined in YAML files with this structure:
- `version` - Version generation (typically from timestamps)
- `variables` - Template variables for step interpolation
- `steps` - Sequential release steps with actions (git, run) and metadata

### Step Types

Each step can have exactly one action type:
- **git** - Git operations (shortlog generation, etc.)
- **run** - Shell command or script execution
- **set_variable** - Capture action output as variable for later steps

### Variable System

Variables are rendered throughout the configuration using template syntax, with access to:
- Environment variables
- Generated version strings
- Outputs from previous steps via `set_variable`

## Development Notes

- No test suite currently exists - tests should be added using pytest
- Configuration files are expected in `release.yaml` by default
- TUI application hardcodes config path to `nogit/release.yaml`
- Git operations use pygit2 library for repository interactions
- All step outputs can be captured and reused in subsequent steps

## IMPORTANT, ALWAYS FOLLOW THESE

- NEVER run the tui because it will mess up the Claude Code interface, ask the user to try it out themselves
