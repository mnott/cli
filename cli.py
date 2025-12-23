#!/usr/bin/env python
# encoding: utf-8
r"""

CLI Generator

Create Python CLIs using Typer + Rich with modern pyproject.toml packaging.

## Overview

Generates production-ready Python command-line tools with:
- Typer for argument parsing and auto-help
- Rich for pretty output and tracebacks
- Self-documenting `doc` command via doc2md
- Modern `pyproject.toml` for dependency management
- `uv` for fast package management

## Installation

```bash
cd dev.cli
uv sync
```

## Usage

```bash
# Create new CLIs
cli new mytool                    # Create in current directory (Tier 2)
cli new mytool --pai              # Create in PAI bin (Tier 1)
cli new mytool --standalone       # Create as standalone tool (Tier 3)
cli new mytool --default run      # With default command (runs when no subcommand)
cli new mytool -s --deps httpx    # Standalone with extra dependency
cli new mytool -s --deps "httpx,beautifulsoup4"  # Multiple deps

# Deploy existing CLI to scripts directory (auto-detects dependencies!)
cli deploy ./weather.py           # Copy to scripts as standalone (Tier 3)
cli deploy ./weather.py --force   # Overwrite if exists
cli deploy ./weather.py --move    # Move instead of copy
cli deploy ./weather.py -n wthr   # Deploy with different name
```

## Commands

- `new` - Create a new CLI from skeleton
- `deploy` - Deploy existing CLI to scripts directory as standalone (Tier 3)
- `doc` - Generate documentation (use `cli doc > README.md`)

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--desc` | `-d` | Short description of the CLI |
| `--pai` | `-p` | Create in PAI bin directory (Tier 1) |
| `--standalone` | `-s` | Create as standalone tool with own repo (Tier 3) |
| `--deps` | | Extra dependencies (comma-separated) |
| `--default` | | Default command name (runs when no subcommand given) |
| `--force` | `-f` | Overwrite if exists |

## Tiers

| Tier | Flag | Location | Use Case |
|------|------|----------|----------|
| 2 (default) | none | Current directory | Project-specific scripts |
| 1 | `--pai` | `~/.claude/bin/` | PAI infrastructure tools |
| 3 | `--standalone` | `$PAI_SCRIPTS_DIR/dev.X/` | Reusable tools with own repo |

## Generated Project Structure (Tier 3)

```
dev.mytool/
├── pyproject.toml     # Dependencies + entry point
├── mytool.py          # Main CLI script
├── README.md          # Generated from docstring
└── .gitignore
```

## Generated CLI Features

Each generated CLI includes:
- Typer for argument parsing with auto-generated help
- Rich for pretty console output and tracebacks
- Self-documenting `doc` command
- Example command to modify or delete

## pyproject.toml

Standalone tools use modern `pyproject.toml` packaging (PEP 517/518/621):

- **Dependencies** defined in `project.dependencies`
- **Entry point** defined in `project.scripts` (e.g., `mytool = "mytool:app"`)
- **Build system** uses hatchling

Run with `uv sync && uv run mytool` or install with `uv pip install -e .`

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

SKELETON_WITH_DEFAULT = r'''#!/usr/bin/env python
# encoding: utf-8
r"""

{name}

{description}

## Overview

## Usage

    {name_lower} [ARGS] [OPTIONS]

Arguments passed directly are forwarded to the `{default_cmd}` command.

## Commands

- `{default_cmd}` - Default command (runs when no command specified)
- `doc` - Generate documentation

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
    no_args_is_help=False,
    help="{description}",
    epilog="To get help about the script, call it with the --help option."
)


#
# Command: {default_cmd_title}
#
@app.command()
def {default_cmd}(
    arg: str = typer.Argument("", help="Argument for {default_cmd}"),
):
    """
    Default command - runs when no subcommand specified.
    """
    console.print(f"[green]Running {default_cmd} with: {{arg}}[/green]")


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
    import sys

    # Get registered command names dynamically
    commands = {{cmd.callback.__name__ for cmd in app.registered_commands if cmd.callback}}
    options = {{"--help", "-h"}}

    # Default to '{default_cmd}' command if first arg isn't a known command or option
    if len(sys.argv) == 1:
        sys.argv.append("{default_cmd}")
    elif sys.argv[1] not in commands | options:
        sys.argv.insert(1, "{default_cmd}")

    try:
        app()
    except SystemExit as e:
        if e.code != 0:
            raise
'''

PYPROJECT_TEMPLATE = '''[project]
name = "{name}"
version = "0.1.0"
description = "{description}"
requires-python = ">=3.10"
dependencies = [
    "typer>=0.15.0",
    "rich>=13.7.1",
    "doc2md>=0.1.0",
]

[project.scripts]
{name} = "{name}:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
'''

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
cd dev.{name}
uv sync
```

## Usage

```bash
uv run {name} --help
# Or after installing in dev mode:
uv pip install -e .
{name} --help
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


def generate_pyproject(name: str, description: str, extra_deps: Optional[str] = None) -> str:
    """Generate pyproject.toml content with optional extra dependencies."""
    content = PYPROJECT_TEMPLATE.format(name=name, description=description)
    if extra_deps:
        # Insert extra deps into the dependencies list
        lines = content.split("\n")
        new_lines = []
        for line in lines:
            new_lines.append(line)
            if '"doc2md>=0.1.0",' in line:
                for dep in extra_deps.split(","):
                    dep = dep.strip()
                    if dep:
                        new_lines.append(f'    "{dep}",')
        content = "\n".join(new_lines)
    return content


# Standard library modules (Python 3.9+) - not exhaustive but covers common cases
STDLIB_MODULES = {
    "abc", "aifc", "argparse", "array", "ast", "asyncio", "atexit", "base64",
    "bdb", "binascii", "binhex", "bisect", "builtins", "bz2", "calendar",
    "cgi", "cgitb", "chunk", "cmath", "cmd", "code", "codecs", "codeop",
    "collections", "colorsys", "compileall", "concurrent", "configparser",
    "contextlib", "contextvars", "copy", "copyreg", "cProfile", "crypt",
    "csv", "ctypes", "curses", "dataclasses", "datetime", "dbm", "decimal",
    "difflib", "dis", "distutils", "doctest", "email", "encodings", "enum",
    "errno", "faulthandler", "fcntl", "filecmp", "fileinput", "fnmatch",
    "fractions", "ftplib", "functools", "gc", "getopt", "getpass", "gettext",
    "glob", "graphlib", "grp", "gzip", "hashlib", "heapq", "hmac", "html",
    "http", "imaplib", "imghdr", "imp", "importlib", "inspect", "io",
    "ipaddress", "itertools", "json", "keyword", "lib2to3", "linecache",
    "locale", "logging", "lzma", "mailbox", "mailcap", "marshal", "math",
    "mimetypes", "mmap", "modulefinder", "multiprocessing", "netrc", "nis",
    "nntplib", "numbers", "operator", "optparse", "os", "ossaudiodev",
    "pathlib", "pdb", "pickle", "pickletools", "pipes", "pkgutil", "platform",
    "plistlib", "poplib", "posix", "posixpath", "pprint", "profile", "pstats",
    "pty", "pwd", "py_compile", "pyclbr", "pydoc", "queue", "quopri", "random",
    "re", "readline", "reprlib", "resource", "rlcompleter", "runpy", "sched",
    "secrets", "select", "selectors", "shelve", "shlex", "shutil", "signal",
    "site", "smtpd", "smtplib", "sndhdr", "socket", "socketserver", "spwd",
    "sqlite3", "ssl", "stat", "statistics", "string", "stringprep", "struct",
    "subprocess", "sunau", "symtable", "sys", "sysconfig", "syslog", "tabnanny",
    "tarfile", "telnetlib", "tempfile", "termios", "test", "textwrap", "threading",
    "time", "timeit", "tkinter", "token", "tokenize", "trace", "traceback",
    "tracemalloc", "tty", "turtle", "turtledemo", "types", "typing", "unicodedata",
    "unittest", "urllib", "uu", "uuid", "venv", "warnings", "wave", "weakref",
    "webbrowser", "winreg", "winsound", "wsgiref", "xdrlib", "xml", "xmlrpc",
    "zipapp", "zipfile", "zipimport", "zlib", "_thread",
}

# Base dependencies already in REQUIREMENTS_TEMPLATE
BASE_DEPS = {"typer", "rich", "doc2md"}


def detect_imports(file_path: Path) -> set[str]:
    """Detect third-party imports from a Python file."""
    import ast

    content = file_path.read_text()
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return set()

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                # Get top-level module
                module = alias.name.split(".")[0]
                imports.add(module)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                module = node.module.split(".")[0]
                imports.add(module)

    # Filter out stdlib and base deps
    third_party = imports - STDLIB_MODULES - BASE_DEPS
    return third_party


def create_cli_file(path: Path, name: str, description: str, default_cmd: Optional[str] = None) -> None:
    """Create CLI file from skeleton."""
    if default_cmd:
        content = SKELETON_WITH_DEFAULT.format(
            name=name.title(),
            name_lower=name.lower(),
            description=description,
            default_cmd=default_cmd,
            default_cmd_title=default_cmd.title(),
        )
    else:
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
    default: str = typer.Option(
        None,
        "--default",
        help="Default command name (e.g., 'run', 'get') - runs when no subcommand given"
    ),
    deps: str = typer.Option(
        None,
        "--deps",
        help="Additional dependencies (comma-separated, e.g., 'httpx,beautifulsoup4')"
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
    Use --default to specify a command that runs when no subcommand is given.
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

        # Create pyproject.toml
        (tool_dir / "pyproject.toml").write_text(generate_pyproject(name, description, deps))
        console.print(f"[dim]Created:[/dim] {tool_dir / 'pyproject.toml'}")

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
    create_cli_file(target, name, description, default)
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
    if default:
        summary += f"[cyan]Default cmd:[/cyan] {default} (runs when no subcommand given)\n"
    if standalone:
        summary += f"""
[cyan]Next steps:[/cyan]
  cd {tool_dir}
  uv sync                    # Install dependencies
  uv run {name} --help       # Run the CLI

[cyan]To push to remote:[/cyan]
  git add .
  git commit -m "Initial version"
  git branch -M main
  git remote add origin <your-remote-url>
  git push -u origin main
"""
    console.print(Panel(summary.strip(), title="CLI Created", border_style="green"))


#
# Command: Deploy
#
@app.command()
def deploy(
    file: Path = typer.Argument(..., help="Path to existing CLI file to deploy"),
    name: str = typer.Option(
        None,
        "--name", "-n",
        help="Name for the tool (defaults to filename without .py)"
    ),
    move: bool = typer.Option(
        False,
        "--move", "-m",
        help="Move instead of copy (deletes original)"
    ),
    force: bool = typer.Option(
        False,
        "--force", "-f",
        help="Overwrite if exists"
    ),
):
    """
    Deploy an existing CLI to scripts directory as standalone tool (Tier 3).

    Takes a local CLI file and sets up full Tier 3 structure:
    git repo, requirements.txt, README.md, .gitignore, and symlink.
    """
    import shutil

    # Resolve the file path
    file = file.resolve()
    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(code=1)

    if not file.suffix == ".py":
        console.print(f"[red]Error:[/red] File must be a .py file")
        raise typer.Exit(code=1)

    # Determine the tool name
    tool_name = name or file.stem

    # Set up paths
    tool_dir = SCRIPTS_DIR / f"dev.{tool_name}"
    target = tool_dir / f"{tool_name}.py"
    symlink = SCRIPTS_DIR / tool_name

    # Check if exists
    if tool_dir.exists() and not force:
        console.print(f"[red]Error:[/red] {tool_dir} already exists. Use --force to overwrite.")
        raise typer.Exit(code=1)

    # Create tool directory
    tool_dir.mkdir(parents=True, exist_ok=True)

    # Copy or move the CLI file
    if move:
        shutil.move(str(file), target)
        console.print(f"[dim]Moved:[/dim] {file} -> {target}")
    else:
        shutil.copy2(file, target)
        console.print(f"[dim]Copied:[/dim] {file} -> {target}")

    # Ensure executable
    make_executable(target)

    # Detect third-party imports and create pyproject.toml
    detected_deps = detect_imports(target)
    deps_str = ",".join(sorted(detected_deps)) if detected_deps else None
    # Read description from docstring if available
    desc = "A command-line tool"
    try:
        import ast
        tree = ast.parse(target.read_text())
        if ast.get_docstring(tree):
            first_line = ast.get_docstring(tree).strip().split("\n")[0]
            if first_line:
                desc = first_line
    except Exception:
        pass
    (tool_dir / "pyproject.toml").write_text(generate_pyproject(tool_name, desc, deps_str))
    if detected_deps:
        console.print(f"[dim]Created:[/dim] {tool_dir / 'pyproject.toml'} (detected: {', '.join(sorted(detected_deps))})")
    else:
        console.print(f"[dim]Created:[/dim] {tool_dir / 'pyproject.toml'}")

    # Generate README from docstring
    try:
        result = subprocess.run(
            ["python", str(target), "doc"],
            capture_output=True,
            text=True,
            cwd=tool_dir
        )
        if result.returncode == 0 and result.stdout.strip():
            (tool_dir / "README.md").write_text(result.stdout)
            console.print(f"[dim]Generated:[/dim] {tool_dir / 'README.md'} (from docstring)")
        else:
            # Fallback if doc command fails
            readme = f"# {tool_name}\n\nDeployed CLI tool.\n"
            (tool_dir / "README.md").write_text(readme)
            console.print(f"[dim]Created:[/dim] {tool_dir / 'README.md'} (basic)")
    except Exception:
        readme = f"# {tool_name}\n\nDeployed CLI tool.\n"
        (tool_dir / "README.md").write_text(readme)
        console.print(f"[dim]Created:[/dim] {tool_dir / 'README.md'} (basic)")

    # Initialize git
    subprocess.run(["git", "init"], cwd=tool_dir, capture_output=True)
    console.print(f"[dim]Initialized:[/dim] git repository")

    # Create .gitignore
    (tool_dir / ".gitignore").write_text(GITIGNORE_TEMPLATE)
    console.print(f"[dim]Created:[/dim] {tool_dir / '.gitignore'}")

    # Create symlink
    if symlink.exists() or symlink.is_symlink():
        symlink.unlink()
    symlink.symlink_to(target)
    console.print(f"[green]Symlinked:[/green] {symlink} -> {target}")

    # Summary
    summary = f"""
[bold]{tool_name}[/bold] deployed as Standalone (Tier 3)

[cyan]Location:[/cyan] {target}
[cyan]Run with:[/cyan] uv run {tool_name} --help

[cyan]Next steps:[/cyan]
  cd {tool_dir}
  uv sync                    # Install dependencies
  uv run {tool_name} --help  # Run the CLI

[cyan]To push to remote:[/cyan]
  git add .
  git commit -m "Initial version"
  git branch -M main
  git remote add origin <your-remote-url>
  git push -u origin main
"""
    console.print(Panel(summary.strip(), title="CLI Deployed", border_style="green"))


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
