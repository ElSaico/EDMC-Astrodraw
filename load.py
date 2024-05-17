import logging
import os
import sqlite3
import tkinter as tk
from tkinter import ttk
from typing import Optional

from theme import theme
from config import appname, config
import myNotebook as nb

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f'{appname}.{plugin_name}')
frame: Optional[tk.Frame] = None

# values outside the index were linearly interpolated; anything beyond 20 is overkill
INDEXED_HEATMAP = [  # TODO verify
    '#000000', '#000080', '#0000ff', '#1515ff', '#2a2aff', '#3f3fff', '#3f4bff',
    '#3f58ff', '#3f65ff', '#3f72ff', '#3f80ff', '#398cff', '#3299ff', '#2ca6ff',
    '#26b3ff', '#1fc0ff', '#19ccff', '#13d9ff', '#0ce6ff', '#06f3ff', '#00ffff',
]


def plugin_start3(plugin_dir: str) -> str:
    return plugin_name


def plugin_stop() -> None:
    logger.info('Stopping EDMC-Astrodraw')


def plugin_app(parent: tk.Frame) -> Optional[tk.Frame]:
    frame = tk.Frame(parent)
    return frame
