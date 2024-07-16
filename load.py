import csv
import io
import itertools
import logging
import os
import re
import requests
import threading
import tkinter as tk
from tkinter import filedialog

from PIL import Image, ImageDraw, ImageTk
from config import appname, user_agent
from theme import theme

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f'{appname}.{plugin_name}')

# values outside the index were linearly interpolated; anything beyond 20 is overkill
INDEXED_HEATMAP = [  # TODO verify
    '#000000', '#000080', '#0000ff', '#1515ff', '#2a2aff', '#3f3fff', '#3f4bff',
    '#3f58ff', '#3f65ff', '#3f72ff', '#3f80ff', '#398cff', '#3299ff', '#2ca6ff',
    '#26b3ff', '#1fc0ff', '#19ccff', '#13d9ff', '#0ce6ff', '#06f3ff', '#00ffff',
]
RE_EDASTRO_UPDATE = re.compile(r"var timestamp_tiles = '(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2})(\d{2})';")


def galactic_x_to_map_x(x):
    return x / 10 + 8192


def galactic_z_to_map_y(z):
    return (z - 25000) / 10 + 8192


class Astrodraw:
    frame: tk.Frame
    heatmap_root: tk.Frame
    heatmap_grid: dict[tuple[int, int], tk.Frame] = {}
    heatmap_images: dict[tuple[int, int], Image.Image] = {}
    # Tk does not keep references to images, so we must store them to avoid garbage collection
    tiles: list[ImageTk.PhotoImage] = []
    coords: list[tuple[int, int]]
    min_x: int
    min_y: int

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

        self.heatmap_root = tk.Frame(self.frame)
        self.heatmap_root.pack(fill=tk.BOTH)

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
        if f := filedialog.askopenfile():
            with f:  # TODO error handling
                self.coords = [(int(x), int(z)) for x, z in csv.reader(f)]
            self.heatmap_images.clear()
            xs, zs = zip(*self.coords)
            self.min_x = int(galactic_x_to_map_x(min(xs)) // 256)
            max_x = int(galactic_x_to_map_x(max(xs)) // 256)
            self.min_y = int(galactic_z_to_map_y(min(zs)) // 256)
            max_y = int(galactic_z_to_map_y(max(zs)) // 256)
            for x in range(self.min_x, max_x + 1):
                for y in range(self.min_y, max_y + 1):
                    # TODO make threaded
                    tile = requests.get(f'https://edastro.b-cdn.net/galmap/tiles/indexedheat/6/{x}/{y}.png')
                    self.heatmap_images[x, y] = Image.open(io.BytesIO(tile.content))
            self.draw_heatmap()

    def draw_heatmap(self):
        self.tiles.clear()
        for child in self.heatmap_root.children.values():
            child.destroy()
        for x, y in self.heatmap_images:
            image = self.heatmap_images[x, y].copy()
            draw = ImageDraw.Draw(image)
            if self.show_drawing.get():
                ...  # TODO map lines to tiles
            if self.show_predict.get():
                ...
            grid_image = ImageTk.PhotoImage(image)
            self.tiles.append(grid_image)
            tk.Label(self.heatmap_root, image=grid_image, borderwidth=0).grid(row=y - self.min_y, column=x - self.min_x)
        theme.update(self.heatmap_root)


plugin = Astrodraw()
plugin_start3 = plugin.start
plugin_stop = plugin.stop
plugin_app = plugin.app
