"""Click entry points for pyproject.toml ``[project.scripts]``.

These are thin wrappers around ``scripts/01_clean_data.py``,
``scripts/02_simulate_training.py``, and ``scripts/03_train_surrogate.py`` so
that ``pip install -e .`` exposes ``tinydcs-clean``, ``tinydcs-simulate``, and
``tinydcs-train`` on the PATH without duplicating logic.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_script(name: str):
    root = Path(__file__).resolve().parent.parent / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""), root)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not locate {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def clean() -> None:
    """tinydcs-clean entry point."""
    _load_script("01_clean_data.py").main(standalone_mode=True)


def simulate() -> None:
    """tinydcs-simulate entry point."""
    _load_script("02_simulate_training.py").main(standalone_mode=True)


def train() -> None:
    """tinydcs-train entry point."""
    _load_script("03_train_surrogate.py").main(standalone_mode=True)
