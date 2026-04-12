# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**yadata** is a YAML-based object database CLI tool. It processes streams of YAML documents through a Unix-pipe-like chain of subcommands, where `!` separates subcommands instead of `|`. Records are YAML-tagged dict subclasses with type checking (via `typeguard`), key generation, and relationship support (one-to-many, many-to-many).

## Build & Development

- **Package manager**: Poetry (`poetry install` to set up)
- **Python**: 3.11+
- **Run CLI**: `poetry run yadata <subcommand> [args] [! <subcommand> [args] ...]`
- **Run all tests**: `python -m pytest`
- **Run a single test**: `python -m pytest tests/command/test_filter.py::test_filter_normal`
- **Debug logging**: Set `YADATA_DEBUG=1` environment variable

## Architecture

### Pipeline Model

The CLI (`yadata/main.py`) parses `sys.argv` splitting on `!` to chain subcommands. Each subcommand is a `YadataCommand` subclass with `data_in`/`data_out` flags indicating whether it consumes/produces a YAML record stream. The first command with `data_in=True` reads from stdin; the last command with `data_out=True` writes to stdout.

### Subcommands (`yadata/command/`)

Each command is a class inheriting `YadataCommand` with class-level `arguments` tuple (of `Argument`/`MexGroup` wrappers around argparse) and an `execute(it)` method that yields records:

| Command | Purpose |
|---------|---------|
| `read`  | Load records from a data directory (no stdin) |
| `merge` | Merge stdin records into a data directory (set/union/delete/extend methods for conflict resolution) |
| `filter`| Keep records matching a Python expression (`eval`) |
| `exec`  | Execute a Python statement on each record |
| `yield` | Evaluate a Python term per record, output the result |
| `sort`  | Sort records by field keys (supports `~field` for reverse) |
| `cast`  | Convert plain dicts to typed Record subclasses |
| `append`| Append strings to a list field |
| `render`| Render records through a Jinja2 template (no YAML output) |
| `run`   | Run a shell command per record with `YADATA_` env vars |

### Record System (`yadata/record.py`)

`Record` is a dict subclass with `MetaRecord` metaclass that auto-registers YAML tags (set `yadata_tag = 'auto'` to use `!ClassName`). Records support:
- Type annotations checked at init and on `__setitem__` via `typeguard`
- Dotted key access (`rec["a.b"]` traverses nested dicts)
- Key generation via `key_format` class attribute or `get_key_prefix()` method
- Merge with conflict resolution methods: `set`, `union`, `extend`, `delete`
- Relationships via `@AddOneToMany` and `@AddManyToMany` decorators

### Custom Types (`_yadata_types`)

Projects using yadata define a `_yadata_types.py` module in their working directory (loaded via `sys.path.append(os.getcwd())`). This module defines `Record` subclasses with YAML tags, type hints, and relationships. The `cast` command references types from this module.

### Data Directory (`yadata/datadir.py`)

`Datadir` loads all `.yaml` files from a directory tree into a list of `Record` objects, indexed by `_key`. Used by `read` and `merge` commands.

### YAML Handling (`yadata/utils/sane_yaml.py`)

Custom YAML dump that orders `_key` first, then `top_fields`, then remaining fields. Handles unicode properly.
