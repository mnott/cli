# cli

CLI Generator


Create Python CLIs using Typer + Rich with a proven skeleton pattern.

## Overview

Generates production-ready Python command-line tools with:
- Typer for argument parsing and auto-help
- Rich for pretty output and tracebacks
- Self-documenting `doc` command via doc2md

## Installation

```bash
uv pip install -r requirements.txt
```

## Usage

```bash
cli new mytool                    # Create in current directory (Tier 2)
cli new mytool --pai              # Create in PAI bin (Tier 1)
cli new mytool --standalone       # Create as standalone tool (Tier 3)
```

## Commands

- `new` - Create a new CLI from skeleton
- `doc` - Generate documentation (use `cli doc > README.md`)

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--desc` | `-d` | Short description of the CLI |
| `--pai` | `-p` | Create in PAI bin directory (Tier 1) |
| `--standalone` | `-s` | Create as standalone tool with own repo (Tier 3) |
| `--force` | `-f` | Overwrite if exists |

## Tiers

| Tier | Flag | Location | Use Case |
|------|------|----------|----------|
| 2 (default) | none | Current directory | Project-specific scripts |
| 1 | `--pai` | `~/.claude/bin/` | PAI infrastructure tools |
| 3 | `--standalone` | `$PAI_SCRIPTS_DIR/dev.X/` | Reusable tools with own repo |

## Generated CLI Features

Each generated CLI includes:
- Typer for argument parsing with auto-generated help
- Rich for pretty console output and tracebacks
- Self-documenting `doc` command
- Example command to modify or delete

## Configuration

Environment variables (set in ~/.zshrc or ~/.claude/.env):
- `PAI_BIN_DIR` - PAI CLIs directory (default: ~/.claude/bin)
- `PAI_SCRIPTS_DIR` - Standalone tools directory
