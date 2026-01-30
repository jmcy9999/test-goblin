# Contributing to XCUITest Goblin

Thanks for your interest in contributing! This document outlines how to get started.

## Ways to Contribute

- **Report bugs** — Open an issue describing the problem
- **Suggest features** — Open an issue with your idea
- **Submit fixes** — Fork, fix, and open a pull request
- **Improve docs** — Clarifications and corrections are always welcome

## Getting Started

### 1. Fork and clone

```bash
git clone https://github.com/YOUR-USERNAME/xcuitest-goblin.git
cd xcuitest-goblin
```

### 2. Set up development environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### 3. Create a branch

```bash
git checkout -b feature/your-feature-name
```

## Development Guidelines

### Code Style

- Follow PEP 8
- Use type hints where practical
- Keep functions focused and small
- Write descriptive commit messages

### Running Tests

```bash
pytest
```

### Running Linters

```bash
black .
flake8
mypy xcuitest_goblin
```

## Pull Request Process

1. **Update tests** — Add tests for new functionality
2. **Update docs** — Update README or docs if needed
3. **Run checks** — Ensure tests and linters pass
4. **Keep it focused** — One feature or fix per PR
5. **Write a clear description** — Explain what and why

### PR Title Format

Use a clear, descriptive title:

- `Add: feature description`
- `Fix: bug description`
- `Docs: what was updated`
- `Refactor: what was changed`

## Reporting Bugs

When reporting a bug, please include:

- XCUITest Goblin version (`xcuitest-goblin --version`)
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Any error messages

## Suggesting Features

When suggesting a feature:

- Check existing issues first
- Describe the use case
- Explain why it would be useful
- Consider how it fits with existing functionality

## Questions?

Open an issue with your question — we're happy to help!
