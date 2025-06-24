# Migrating to `uv` for Virtual Environments and Package Management

## Overview

`uv` is a modern, ultra-fast Python package manager and virtual environment tool designed to be a drop-in replacement for `pip`, `venv`, and `pip-tools`. It offers significant speed improvements, deterministic builds, and a streamlined workflow for managing dependencies in Python projects.

This document outlines the benefits of using `uv`, how it compares to traditional tools like `requirements.txt` and `venv`, and provides a migration path for the TruLedgr project.

---

## Why Consider `uv`?

- **Speed:** `uv` is written in Rust and is much faster than `pip` and `venv`.
- **Deterministic:** Lockfiles ensure reproducible builds across all environments.
- **Unified Workflow:** Handles virtual environments, dependency resolution, and installation in one tool.
- **Modern Features:** Supports PEP 582, editable installs, and more.

---

## Current Workflow (Traditional)

- Use `python -m venv .venv` to create a virtual environment.
- Use `pip install -r requirements.txt` to install dependencies.
- Manually update `requirements.txt` for dependency changes.

### Drawbacks
- Dependency resolution can be slow and non-deterministic.
- Multiple tools and files to manage (`venv`, `requirements.txt`, `pip-tools`, etc.).
- No built-in lockfile for reproducibility.

---

## The `uv` Workflow

- Use `uv venv` to create and manage virtual environments.
- Use `uv pip install ...` or `uv pip sync` to install and sync dependencies.
- Use `uv pip compile` to generate lockfiles for deterministic builds.
- Manage dependencies in `pyproject.toml` and lockfiles, not `requirements.txt`.

### Example Commands
```sh
# Create a virtual environment
uv venv .venv

# Install dependencies from pyproject.toml
uv pip install

# Add a new package
uv pip install fastapi

# Compile a lockfile
uv pip compile

# Sync environment to lockfile
uv pip sync
```

---

## Migration Plan

1. **Add all dependencies to `pyproject.toml`.**
2. **Generate a lockfile with `uv pip compile`.**
3. **Remove `requirements.txt` from the repo.**
4. **Update documentation and scripts to use `uv` commands.**
5. **Test the workflow across all supported platforms.**

---

## References
- [uv documentation](https://github.com/astral-sh/uv)
- [PEP 582](https://peps.python.org/pep-0582/)

---

By migrating to `uv`, TruLedgr will benefit from faster, more reliable, and modern Python dependency management.
