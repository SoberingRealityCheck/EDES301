"""
App discovery and loading.

scan_apps() scans the apps/ directory for valid app packages and returns
a list of AppEntry objects that the MenuState can display and that
AppRunnerState can instantiate.

A valid app directory must contain:
    app.py  — defines class App(BaseApp)

Optional but used if present:
    name.txt  — display name for the menu (falls back to directory name)
    icon.npy  — 32x32x3 uint8 numpy array for the menu icon
                (falls back to a solid colour placeholder)
"""

import os
import importlib.util
from dataclasses import dataclass
from pathlib import Path
from typing import Type

import numpy as np


_PLACEHOLDER_COLOURS = [
    (200,  60,  60),   # red
    ( 60, 200,  60),   # green
    ( 60,  60, 200),   # blue
    (200, 200,  60),   # yellow
]


@dataclass
class AppEntry:
    """Metadata for one discovered app."""
    name:      str           # display name shown in the menu
    icon:      np.ndarray    # shape (32,32,3) uint8
    app_class: Type          # class App(BaseApp) — NOT yet instantiated
    app_dir:   Path          # absolute path to the app directory


def scan_apps(apps_dir: Path) -> list:
    """
    Scan apps_dir for subdirectories containing app.py with class App.

    Args:
        apps_dir : absolute path to the apps/ directory

    Returns:
        List of AppEntry, sorted alphabetically by directory name.
        Prints a warning and skips invalid directories.
    """
    entries = []

    for dir_name in sorted(os.listdir(apps_dir)):
        app_path = apps_dir / dir_name
        if not app_path.is_dir():
            continue

        app_py = app_path / "app.py"
        if not app_py.exists():
            print(f"[apps_loader] Warning: {dir_name}/ has no app.py — skipping")
            continue

        # Dynamically import app.py
        spec   = importlib.util.spec_from_file_location(dir_name, app_py)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            print(f"[apps_loader] Warning: failed to import {dir_name}/app.py: {e}")
            continue

        if not hasattr(module, "App"):
            print(f"[apps_loader] Warning: {dir_name}/app.py has no App class — skipping")
            continue

        # Name
        name_file = app_path / "name.txt"
        name = name_file.read_text().strip() if name_file.exists() else dir_name

        # Icon — load or generate placeholder
        icon_file = app_path / "icon.npy"
        if icon_file.exists():
            try:
                icon = np.load(icon_file)
                if icon.shape != (32, 32, 3):
                    raise ValueError("Wrong shape")
            except Exception as e:
                print(f"[apps_loader] Warning: bad icon for {dir_name}: {e} — using placeholder")
                icon = _make_placeholder_icon(len(entries))
        else:
            icon = _make_placeholder_icon(len(entries))

        entries.append(AppEntry(
            name      = name,
            icon      = icon,
            app_class = module.App,
            app_dir   = app_path,
        ))
        print(f"[apps_loader] Loaded: {name}")

    return entries


def _make_placeholder_icon(idx: int) -> np.ndarray:
    """Return a 32x32x3 solid-colour icon using a rotating palette."""
    color = _PLACEHOLDER_COLOURS[idx % len(_PLACEHOLDER_COLOURS)]
    return np.full((32, 32, 3), color, dtype=np.uint8)
