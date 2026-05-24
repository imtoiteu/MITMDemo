"""
reset_lab.py — Reset the Security Awareness Demo lab to a clean state.

What this script does:
  1. Removes tlskeys/sslkeys.log  (old TLS session keys)
  2. Removes tlskeys/chrome_profile/  (old Chrome demo profile)
  3. Recreates tlskeys/ and an empty sslkeys.log
  4. Prints next steps

Usage:
    python scripts/reset_lab.py

This is safe to run between classroom sessions to ensure students
start from a known-clean state with no residual key material.
"""

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# ── Colour helpers ────────────────────────────────────────────────────
import platform as _plt

from app.config import settings

_WIN = _plt.system() == "Windows"


def _c(code: str, text: str) -> str:
    """Wrap text in ANSI colour if terminal supports it.

    Args:
        code: ANSI escape code.
        text: Text to colour.

    Returns:
        Coloured or plain string.
    """
    if _WIN:
        return text
    return f"\033[{code}m{text}\033[0m"


def GREEN(t: str) -> str:  # noqa: N802
    """Return green-coloured text.

    Args:
        t: Input text.

    Returns:
        ANSI-coloured string.
    """
    return _c("92", t)


def YELLOW(t: str) -> str:  # noqa: N802
    """Return yellow-coloured text.

    Args:
        t: Input text.

    Returns:
        ANSI-coloured string.
    """
    return _c("93", t)


def CYAN(t: str) -> str:  # noqa: N802
    """Return cyan-coloured text.

    Args:
        t: Input text.

    Returns:
        ANSI-coloured string.
    """
    return _c("96", t)


def BOLD(t: str) -> str:  # noqa: N802
    """Return bold text.

    Args:
        t: Input text.

    Returns:
        ANSI-coloured string.
    """
    return _c("1", t)


def DIM(t: str) -> str:  # noqa: N802
    """Return dimmed text.

    Args:
        t: Input text.

    Returns:
        ANSI-coloured string.
    """
    return _c("2", t)


def reset_lab(project_root: Path) -> None:
    """Perform a full lab reset.

    Args:
        project_root: Absolute path to the project root directory.

    Returns:
        None
    """
    keylog_path = project_root / settings.keylog_file
    tlskeys_dir = project_root / settings.tlskeys_dir
    chrome_profile = tlskeys_dir / "chrome_profile"

    print(BOLD(CYAN("\n🔄  Resetting Security Awareness Demo Lab …\n")))

    # 1. Remove Chrome profile
    if chrome_profile.exists():
        shutil.rmtree(chrome_profile, ignore_errors=True)
        print(GREEN(f"   ✓  Removed Chrome profile: {chrome_profile}"))
    else:
        print(DIM("   –  Chrome profile not found (skipped)"))

    # 2. Remove old TLS key log
    if keylog_path.exists():
        keylog_path.unlink()
        print(GREEN(f"   ✓  Removed TLS key log: {keylog_path}"))
    else:
        print(DIM("   –  TLS key log not found (skipped)"))

    # 3. Recreate directory and empty log file
    tlskeys_dir.mkdir(parents=True, exist_ok=True)
    keylog_path.touch()
    print(GREEN(f"   ✓  Created fresh key log: {keylog_path}"))

    # 4. Print summary
    print()
    print(BOLD("  ✅  Lab reset complete!"))
    print()
    print(BOLD("  Next steps:"))
    print(f"      1. Restart the demo:   {CYAN('python run.py')}")
    print(
        "      2. In Wireshark:      clear existing captures"
        " (Ctrl+E → restart)"
    )
    print(
        f"      3. Reload key log:    "
        f"Preferences → TLS → (Pre)-Master-Secret log → "
        f"{CYAN(str(keylog_path))}"
    )
    print()


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.resolve()
    reset_lab(project_root)
