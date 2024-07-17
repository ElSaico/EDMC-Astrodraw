import collections
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
from plug import show_error

plugin_name = os.path.basename(os.path.dirname(__file__))
logger = logging.getLogger(f'{appname}.{plugin_name}')

INDEXED_HEATMAP = [  # only a small subset needed; 20 is already way past overkill for our purposes
    (0,    0,   0),  (0,   0, 128),  (0,   0, 255), (21,  21, 255), (42,  42, 255), (63,  63, 255), (63,  75, 255),
    (63,  88, 255), (63, 101, 255), (63, 114, 255), (63, 127, 255), (56, 139, 255), (50, 152, 255), (44, 165, 255),
    (37, 178, 255), (31, 191, 255), (25, 203, 255), (18, 216, 255), (12, 229, 255),  (6, 242, 255),  (0, 255, 255),
]
TILE_SIZE = 256
RE_EDASTRO_UPDATE = re.compile(r"var timestamp_tiles = '(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2})(\d{2})';")


def galactic_x_to_map_x(x: int):
    return int(x // 10) + 8192


def galactic_z_to_map_y(z: int):
    return int((z - 25000) // 10) + 8192


# TODO other zoom levels
class Astrodraw:
    frame: tk.Frame
    heatmap: Image.Image = None
    display_lbl: tk.Label
    # Tk does not keep references to images, so we need one to prevent garbage collection
    display_img: ImageTk.PhotoImage
    coords: list[tuple[int, int]]
    size: tuple[int, int]
    bounds: tuple[int, int, int, int]
    xmin: int
    ymin: int
    discovered_map: dict[tuple[int, int], 0] = {}
    discovered_player: collections.Counter[tuple[int, int]] = collections.Counter()

    def __init__(self):
        self.thread_update = threading.Thread(target=self.worker_update, name='Astrodraw-Update')
        self.thread_update.daemon = True
        self.updated: str = 'Loading...'
        self.heatmap_mode = tk.StringVar(value='default')
        self.heatmap_mode.trace_add('write', lambda _, __, ___: self.draw_heatmap())
        self.session = requests.Session()
        self.session.headers['User-Agent'] = user_agent

    def start(self, plugin_dir: str):
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

        self.display_lbl = tk.Label(self.frame)
        self.display_lbl.pack(fill=tk.BOTH)

        commands_frm = tk.Frame(self.frame)
        commands_frm.pack(fill=tk.X)
        tk.Button(commands_frm, text='Load file', command=self.load_file).pack(side=tk.LEFT)
        # radiobutton labels are not themed properly
        tk.Radiobutton(commands_frm, variable=self.heatmap_mode, value='default').pack(side=tk.LEFT)
        tk.Label(commands_frm, text='Default').pack(side=tk.LEFT)
        tk.Radiobutton(commands_frm, variable=self.heatmap_mode, value='drawing').pack(side=tk.LEFT)
        tk.Label(commands_frm, text='Drawing').pack(side=tk.LEFT)
        tk.Radiobutton(commands_frm, variable=self.heatmap_mode, value='estimate').pack(side=tk.LEFT)
        tk.Label(commands_frm, text='Estimate').pack(side=tk.LEFT)

        self.frame.bind('<<AstrodrawUpdate>>', lambda e: updated_lbl.configure(text=self.updated))
        self.thread_update.start()
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
            try:
                with f:
                    self.coords = [(galactic_x_to_map_x(int(x)), galactic_z_to_map_y(int(z))) for x, z in csv.reader(f)]
            except ValueError:
                show_error('AstroDraw: Wrong file format')
                return
            xs, ys = zip(*self.coords)
            self.xmin = min(xs)
            self.ymin = min(ys)
            xmax = max(xs)
            ymax = max(ys)
            tile_xmin = int(self.xmin // TILE_SIZE)
            tile_xmax = int(xmax // TILE_SIZE)
            tile_ymin = int(self.ymin // TILE_SIZE)
            tile_ymax = int(ymax // TILE_SIZE)
            offset_x = self.xmin % TILE_SIZE
            offset_y = self.ymin % TILE_SIZE
            self.discovered_map.clear()
            self.size = (xmax-self.xmin+1, ymax-self.ymin+1)
            self.bounds = (offset_x, offset_y, xmax-self.xmin+offset_x, ymax-self.ymin+offset_y)
            self.heatmap = Image.new('RGB', (TILE_SIZE * (tile_xmax-tile_xmin+1), TILE_SIZE * (tile_ymax-tile_ymin+1)))
            for x in range(tile_xmin, tile_xmax + 1):
                for y in range(tile_ymin, tile_ymax + 1):  # TODO make threaded
                    tile = requests.get(f'https://edastro.b-cdn.net/galmap/tiles/indexedheat/6/{x}/{y}.png')
                    with Image.open(io.BytesIO(tile.content)) as img:
                        self.heatmap.paste(img, ((x-tile_xmin) * TILE_SIZE, (y-tile_ymin) * TILE_SIZE))
            pixels = self.heatmap.load()
            for x in range(self.heatmap.width):
                for y in range(self.heatmap.height):
                    try:
                        self.discovered_map[x, y] = INDEXED_HEATMAP.index(pixels[x, y])
                    except ValueError:
                        logger.debug(f'Large heatmap index found: {pixels[x, y]}')
            self.draw_heatmap()

    def draw_heatmap(self):
        if not self.heatmap:
            return
        image = self.heatmap.transform(self.size, Image.Transform.EXTENT, self.bounds)
        draw = ImageDraw.Draw(image)
        match self.heatmap_mode.get():
            case 'drawing':
                for (x1, y1), (x2, y2) in itertools.pairwise(self.coords):
                    draw.line((x1-self.xmin, y1-self.ymin, x2-self.xmin, y2-self.ymin), fill=(255, 255, 255))
            # TODO estimate
        self.display_img = ImageTk.PhotoImage(image)
        self.display_lbl['image'] = self.display_img


plugin = Astrodraw()
plugin_start3 = plugin.start
plugin_stop = plugin.stop
plugin_app = plugin.app
