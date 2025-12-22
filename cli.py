#!/usr/bin/env python
# encoding: utf-8
r"""

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

"""

#
# Imports
#
from pathlib import Path
from typing import Optional
import os
import subprocess
import stat

from rich import print
from rich import traceback
from rich import pretty
from rich.console import Console
from rich.panel import Panel
import typer

pretty.install()
traceback.install()
console = Console()

app = typer.Typer(
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=True,
    help="Create Python CLIs using Typer + Rich",
    epilog="To get help about the script, call it with the --help option."
)

#
# Constants
#
SKELETON_PATH = Path.home() / ".claude" / "Skills" / "CreateCLI" / "skeleton.py"
PAI_BIN_DIR = Path(os.getenv("PAI_BIN_DIR", str(Path.home() / ".claude" / "bin")))
SCRIPTS_DIR = Path(os.getenv("PAI_SCRIPTS_DIR", str(Path.home() / "Cloud" / "Development" / "scripts")))

#
# Skeleton template (embedded for independence)
#
SKELETON = r'''#!/usr/bin/env python
# encoding: utf-8
r"""

{name}

{description}

## Overview

## Commands

## Configuration

"""

#
# Imports
#
from rich import print
from rich import traceback
from rich import pretty
from rich.console import Console
import typer

pretty.install()
traceback.install()
console = Console()

app = typer.Typer(
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=True,
    help="{description}",
    epilog="To get help about the script, call it with the --help option."
)


#
# Command: Example
#
@app.command()
def example(
    name: str = typer.Argument(..., help="Name to greet"),
    loud: bool = typer.Option(False, "--loud", "-l", help="Shout the greeting"),
):
    """
    Example command - delete and replace with your own.
    """
    greeting = f"Hello, {{name}}!"
    if loud:
        greeting = greeting.upper()
    console.print(f"[green]{{greeting}}[/green]")


#
# Command: Doc
#
@app.command()
def doc(
    ctx: typer.Context,
    title: str = typer.Option(None, help="The title of the document"),
    toc: bool = typer.Option(False, help="Whether to create a table of contents"),
) -> None:
    """
    Re-create the documentation and write it to the output file.
    """
    import importlib
    import importlib.util
    import sys
    import os
    import doc2md

    def import_path(path):
        module_name = os.path.basename(path).replace("-", "_")
        spec = importlib.util.spec_from_loader(
            module_name,
            importlib.machinery.SourceFileLoader(module_name, path),
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.modules[module_name] = module
        return module

    mod_name = os.path.basename(__file__)
    if mod_name.endswith(".py"):
        mod_name = mod_name.rsplit(".py", 1)[0]
    atitle = title or mod_name.replace("_", "-")
    module = import_path(__file__)
    docstr = module.__doc__
    result = doc2md.doc2md(docstr, atitle, toc=toc, min_level=0)
    print(result)


#
# Main function
#
if __name__ == "__main__":
    try:
        app()
    except SystemExit as e:
        if e.code != 0:
            raise
'''

REQUIREMENTS_TEMPLATE = """typer>=0.15.0
rich>=13.7.1
doc2md>=0.1.0
"""

GITIGNORE_TEMPLATE = """# macOS
.DS_Store

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv/
env/
venv/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Claude Code
.claude/

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.nox/

# Logs
*.log
"""

README_TEMPLATE = """# {name}

{description}

## Installation

```bash
uv pip install -r requirements.txt
```

## Usage

```bash
./{name}.py --help
```

## Commands

- `example` - Example command (replace with your own)
- `doc` - Generate documentation
"""


#
# Helpers
#
def make_executable(path: Path) -> None:
    """Add executable permission to file."""
    current = path.stat().st_mode
    path.chmod(current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def create_cli_file(path: Path, name: str, description: str) -> None:
    """Create CLI file from skeleton."""
    content = SKELETON.format(name=name.title(), description=description)
    path.write_text(content)
    make_executable(path)


#
# Command: New
#
@app.command()
def new(
    name: str = typer.Argument(..., help="Name of the CLI to create"),
    description: str = typer.Option(
        "A command-line tool",
        "--desc", "-d",
        help="Short description of the CLI"
    ),
    pai: bool = typer.Option(
        False,
        "--pai", "-p",
        help="Create in PAI bin directory (Tier 1)"
    ),
    standalone: bool = typer.Option(
        False,
        "--standalone", "-s",
        help="Create as standalone tool with own repo (Tier 3)"
    ),
    force: bool = typer.Option(
        False,
        "--force", "-f",
        help="Overwrite if exists"
    ),
):
    """
    Create a new CLI from skeleton.

    By default, creates in current directory (Tier 2 - Project CLI).
    Use --pai for PAI infrastructure CLIs, --standalone for full repos.
    """
    if pai and standalone:
        console.print("[red]Error:[/red] Cannot use both --pai and --standalone")
        raise typer.Exit(code=1)

    # Determine target path based on tier
    if standalone:
        # Tier 3: Full standalone tool
        tool_dir = SCRIPTS_DIR / f"dev.{name}"
        target = tool_dir / f"{name}.py"
        symlink = SCRIPTS_DIR / name
    elif pai:
        # Tier 1: PAI bin
        target = PAI_BIN_DIR / f"{name}.py"
        tool_dir = None
        symlink = None
    else:
        # Tier 2: Current directory
        target = Path.cwd() / f"{name}.py"
        tool_dir = None
        symlink = None

    # Check if exists
    if target.exists() and not force:
        console.print(f"[red]Error:[/red] {target} already exists. Use --force to overwrite.")
        raise typer.Exit(code=1)

    # Create standalone directory structure
    if standalone:
        if tool_dir.exists() and not force:
            console.print(f"[red]Error:[/red] {tool_dir} already exists. Use --force to overwrite.")
            raise typer.Exit(code=1)

        tool_dir.mkdir(parents=True, exist_ok=True)

        # Create requirements.txt
        (tool_dir / "requirements.txt").write_text(REQUIREMENTS_TEMPLATE)
        console.print(f"[dim]Created:[/dim] {tool_dir / 'requirements.txt'}")

        # Create README.md
        readme_content = README_TEMPLATE.format(name=name, description=description)
        (tool_dir / "README.md").write_text(readme_content)
        console.print(f"[dim]Created:[/dim] {tool_dir / 'README.md'}")

        # Initialize git
        subprocess.run(["git", "init"], cwd=tool_dir, capture_output=True)
        console.print(f"[dim]Initialized:[/dim] git repository")

        # Create .gitignore
        (tool_dir / ".gitignore").write_text(GITIGNORE_TEMPLATE)
        console.print(f"[dim]Created:[/dim] {tool_dir / '.gitignore'}")

    # Create the CLI file
    create_cli_file(target, name, description)
    console.print(f"[green]Created:[/green] {target}")

    # Create symlink for standalone
    if standalone and symlink:
        if symlink.exists() or symlink.is_symlink():
            symlink.unlink()
        symlink.symlink_to(target)
        console.print(f"[green]Symlinked:[/green] {symlink} -> {target}")

    # Summary panel
    tier_name = "Standalone (Tier 3)" if standalone else "PAI (Tier 1)" if pai else "Project (Tier 2)"
    summary = f"""
[bold]{name}[/bold] created as {tier_name}

[cyan]Location:[/cyan] {target}
[cyan]Run with:[/cyan] {"" if standalone else "./"}{name}{"" if standalone else ".py"} --help
"""
    if standalone:
        summary += f"""
[cyan]Next steps:[/cyan]
  cd {tool_dir}
  uv pip install -r requirements.txt
"""
    console.print(Panel(summary.strip(), title="CLI Created", border_style="green"))


#
# Command: Doc
#
@app.command()
def doc(
    ctx: typer.Context,
    title: str = typer.Option(None, help="The title of the document"),
    toc: bool = typer.Option(False, help="Whether to create a table of contents"),
) -> None:
    """
    Re-create the documentation and write it to the output file.
    """
    import importlib
    import importlib.util
    import sys
    import doc2md

    def import_path(path):
        module_name = os.path.basename(path).replace("-", "_")
        spec = importlib.util.spec_from_loader(
            module_name,
            importlib.machinery.SourceFileLoader(module_name, path),
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.modules[module_name] = module
        return module

    mod_name = os.path.basename(__file__)
    if mod_name.endswith(".py"):
        mod_name = mod_name.rsplit(".py", 1)[0]
    atitle = title or mod_name.replace("_", "-")
    module = import_path(__file__)
    docstr = module.__doc__
    result = doc2md.doc2md(docstr, atitle, toc=toc, min_level=0)
    print(result)


#
# Main function
#
if __name__ == "__main__":
    try:
        app()
    except SystemExit as e:
        if e.code != 0:
            raise
