import logging
import os
import sqlite3
import tkinter as tk
from tkinter import ttk
from typing import Optional

from theme import theme
from config import appname, applongname, appcmdname, appversion, copyright, config
import myNotebook as nb

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f'{appname}.{plugin_name}')
frame: Optional[tk.Frame] = None


def plugin_start3(plugin_dir: str) -> str:
    return plugin_name


def plugin_stop() -> None:
    logger.info('Stopping EDMC-Astrodraw')


def plugin_app(parent: tk.Frame) -> Optional[tk.Frame]:
    frame = tk.Frame(parent)
    return frame
