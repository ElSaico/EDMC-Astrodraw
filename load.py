import logging
import os
import re
import requests
import sqlite3
import threading
import tkinter as tk
from typing import Optional

from theme import theme
from config import appname, config, user_agent

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f'{appname}.{plugin_name}')

# values outside the index were linearly interpolated; anything beyond 20 is overkill
INDEXED_HEATMAP = [  # TODO verify
    '#000000', '#000080', '#0000ff', '#1515ff', '#2a2aff', '#3f3fff', '#3f4bff',
    '#3f58ff', '#3f65ff', '#3f72ff', '#3f80ff', '#398cff', '#3299ff', '#2ca6ff',
    '#26b3ff', '#1fc0ff', '#19ccff', '#13d9ff', '#0ce6ff', '#06f3ff', '#00ffff',
]
RE_EDASTRO_UPDATE = re.compile(r"var timestamp_tiles = '(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2})(\d{2})';")


class Astrodraw:
    frame: Optional[tk.Frame] = None

    def __init__(self):
        self.thread_update = threading.Thread(target=self.worker_update, name='Astrodraw-Update')
        self.thread_update.daemon = True
        self.conf_update = tk.StringVar(value=config.get_str('astrodraw_updated', default='Loading...'))
        self.show_drawing = tk.BooleanVar(value=False)
        self.show_predict = tk.BooleanVar(value=False)
        self.session = requests.Session()
        self.session.headers['User-Agent'] = user_agent

    def start(self, plugin_dir: str):
        self.thread_update.start()
        return plugin_name

    def stop(self):
        self.thread_update.join()
        self.session.close()

    def app(self, parent: tk.Frame):
        self.frame = tk.Frame(parent)
        tk.Label(self.frame, text='EDAstro updated:').grid(row=0, sticky=tk.W)
        tk.Label(self.frame, textvariable=self.conf_update).grid(row=0, column=1, columnspan=2, sticky=tk.W)
        heatmap = tk.Frame(self.frame)
        heatmap.grid(row=1, columnspan=3)
        tk.Button(self.frame, text='Load file', command=self.load_file).grid(row=2, column=0)
        tk.Checkbutton(self.frame, text='Drawing', variable=self.show_drawing).grid(row=2, column=1)
        tk.Checkbutton(self.frame, text='Prediction', variable=self.show_predict).grid(row=2, column=2)
        theme.update(self.frame)
        return self.frame

    def worker_update(self):
        logger.info('Fetching timestamp of latest EDAstro update...')
        response = self.session.get('https://edastro.com/galmap/galmap.js')
        updated = RE_EDASTRO_UPDATE.search(response.text)
        y, m, d, h, M, s = updated.groups()
        self.conf_update.set(f'{y}-{m}-{d} {h}:{M}:{s}')
        logger.info('EDAstro latest update timestamp set')

    def load_file(self):
        ...


plugin = Astrodraw()
plugin_start3 = plugin.start
plugin_stop = plugin.stop
plugin_app = plugin.app
