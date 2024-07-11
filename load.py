import logging
import os
import re
import requests
import threading
import tkinter as tk
from typing import Optional

from config import appname, user_agent

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
        self.updated: str = 'Loading...'
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
        updated_frm = tk.Frame(self.frame)
        updated_frm.pack(fill=tk.X)
        tk.Label(updated_frm, text='EDAstro updated:').pack(side=tk.LEFT)
        updated_lbl = tk.Label(updated_frm, text=self.updated)
        updated_lbl.pack(fill=tk.X, side=tk.LEFT)

        heatmap = tk.Frame(self.frame)
        heatmap.pack(fill=tk.BOTH)

        commands_frm = tk.Frame(self.frame)
        commands_frm.pack(fill=tk.X)
        tk.Button(commands_frm, text='Load file', command=self.load_file).pack(side=tk.LEFT)
        # checkbutton labels are not themed properly
        tk.Checkbutton(commands_frm, variable=self.show_drawing).pack(side=tk.LEFT)
        tk.Label(commands_frm, text='Drawing').pack(side=tk.LEFT)
        tk.Checkbutton(commands_frm, variable=self.show_predict).pack(side=tk.LEFT)
        tk.Label(commands_frm, text='Prediction').pack(side=tk.LEFT)

        self.frame.bind('<<AstrodrawUpdate>>', lambda e: updated_lbl.configure(text=self.updated))
        return self.frame

    def worker_update(self):
        logger.info('Fetching timestamp of latest EDAstro update...')
        response = self.session.get('https://edastro.com/galmap/galmap.js')
        updated = RE_EDASTRO_UPDATE.search(response.text)
        y, m, d, h, M, s = updated.groups()
        self.updated = f'{y}-{m}-{d} {h}:{M}:{s}'
        self.frame.event_generate('<<AstrodrawUpdate>>')
        logger.info('EDAstro latest update timestamp set')

    def load_file(self):
        ...


plugin = Astrodraw()
plugin_start3 = plugin.start
plugin_stop = plugin.stop
plugin_app = plugin.app
