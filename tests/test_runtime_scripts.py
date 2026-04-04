from __future__ import annotations

import os
from pathlib import Path
import subprocess


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_resolve_python_prefers_supported_interpreter(tmp_path: Path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _write_fake_python(bin_dir / "python3", version="3.8.18", supported=False)
    _write_fake_python(bin_dir / "python3.11", version="3.11.9", supported=True)

    result = subprocess.run(
        ["/bin/sh", "scripts/resolve_python.sh"],
        cwd=REPO_ROOT,
        env=_script_env(bin_dir),
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == str(bin_dir / "python3.11")


def test_resolve_python_reports_incompatible_versions(tmp_path: Path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _write_fake_python(bin_dir / "python3", version="3.8.18", supported=False)
    _write_fake_python(bin_dir / "python", version="3.9.19", supported=False)

    result = subprocess.run(
        ["/bin/sh", "scripts/resolve_python.sh"],
        cwd=REPO_ROOT,
        env=_script_env(bin_dir),
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "Python 3.11+" in result.stderr
    assert "python3=3.8.18" in result.stderr
    assert "python=3.9.19" in result.stderr


def test_run_cli_wrapper_executes_help():
    result = subprocess.run(
        ["/bin/sh", "scripts/run_cli.sh", "--help"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert "paper-daily-fetch" in result.stdout
    assert "discover" in result.stdout


def _script_env(bin_dir: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = str(bin_dir)
    env["PAPER_DAILY_FETCH_PYTHON_CANDIDATES"] = "python3.11 python3.10 python3.9 python3.8 python3 python"
    return env


def _write_fake_python(path: Path, *, version: str, supported: bool) -> None:
    support_exit = "0" if supported else "1"
    path.write_text(
        "#!/bin/sh\n"
        "if [ \"$1\" = \"-c\" ]; then\n"
        "  case \"$2\" in\n"
        f"    *\"print(f\\\"{{sys.version_info.major}}.{{sys.version_info.minor}}.{{sys.version_info.micro}}\\\")\"*)\n"
        f"      echo \"{version}\"\n"
        "      exit 0\n"
        "      ;;\n"
        "    *\"sys.version_info >= (3, 11)\"*)\n"
        f"      exit {support_exit}\n"
        "      ;;\n"
        "  esac\n"
        "fi\n"
        "exit 1\n"
    )
    path.chmod(0o755)
