from statistics import mean
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union
import math
import bisect
import pygame
import pygame_gui
from pygame_gui.elements import UITextBox
from RssiSignal import RssiSignal

from localization import min_max, trilaterate

import asyncio

from pygame.locals import RESIZABLE
from pygame import Rect
from Anchor import Anchor

from custom_ui_elements.AnchorButton import AnchorButton
from custom_ui_elements.AnchorSettingsWindow import AnchorSettingsWindow
from custom_ui_elements.LearningSettingsWindow import LearningSettingsWindow
from custom_ui_elements.GeneralSettingsWindow import GeneralSettingsWindow
from SignalGenerator import SignalGenerator
from SignalReader import BeaconSignal, SignalReader

from NN.wrapper import Wrapper

import numpy as np

vae = Wrapper()
vae_counter = np.zeros((4))

ANCHORS: List[Anchor] = [
    Anchor((0, 0), name="A1", ssid="sy25-A1", n=2.5, m=-42, color=(0, 255, 0), num=1
    ),
    Anchor(
        (4.5, 0), name="A2", ssid="sy25-A2", n=2.2, m=-33, color=(255, 0, 0), num=2
    ),
    Anchor(
        (0, 6.5), name="A3", ssid="sy25-A3", n=2.2, m=-41, color=(0, 0, 255), num=3
    ),
    Anchor(
        (4.5, 6.5),
        name="A4",
        ssid="sy25-A4",
        n=2.0,
        m=-50,
        color=(255, 255, 0),
        num=4
    ),
]


# _new_signals.append(r)
class App:
    PANEL_WIDTH = 200
    INITIAL_SCREEN_SIZE = (1000, 800)

    def __init__(self) -> None:
        pygame.init()

        self.pix_per_meter_scale = 100
        self.viewport_center_pos = (2.3, 3.3)

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(self.INITIAL_SCREEN_SIZE, RESIZABLE)
        self.is_running = True

        self.manager = pygame_gui.UIManager(self.INITIAL_SCREEN_SIZE)
        self.anchor_settings_window = AnchorSettingsWindow(
            Rect(0, 0, self.PANEL_WIDTH, 200), visible=False
        )
        self.learning_settings_window = LearningSettingsWindow(
            Rect(0, 200, self.PANEL_WIDTH, 220), visible=False
        )

        self.settings_window = GeneralSettingsWindow(
            Rect(
                self.INITIAL_SCREEN_SIZE[0] - self.PANEL_WIDTH, 0, self.PANEL_WIDTH, 310
            )
        )

        self.position_log_box = UITextBox(
            "",
            Rect(-300, -200, 300, 200),
            anchors={"bottom": "bottom", "right": "right"},
            starting_height=2
        )
        self.signal_log_box = UITextBox(
            "", Rect(0, -200, 300, 200), anchors={"bottom": "bottom", "left": "left"}, starting_height=2
        )

        self.canvas = pygame.Surface(self.INITIAL_SCREEN_SIZE)

        self.anchors: List[Anchor] = ANCHORS

        self.anchor_buttons: List[AnchorButton] = []

        for anchor in self.anchors:
            btn = AnchorButton(anchor=anchor)
            self.anchor_buttons.append(btn)

        self.canvas_being_dragged: bool = False
        self.canvas_has_moved: bool = False

        self.dragged_anchor: Anchor | None = None
        self.dragged_anchor_pos: Tuple[float, float] = (0.0, 0.0)

        self.selected_anchor: Optional[Anchor] = None

        self.signals_sorted_by_age: List[RssiSignal] = []

        self.render_age: float = 10

    def set_resolution(self, resolution: Tuple[int, int]):
        self.manager.set_window_resolution(resolution)
        self.canvas = pygame.Surface(resolution)

    def select_anchor(self, anchor: Optional[Anchor]):
        self.selected_anchor = anchor
        self.anchor_settings_window.set_anchor(anchor)

        if anchor is None:
            self.anchor_settings_window.hide()
        else:
            self.anchor_settings_window.show()

    def process_events(self, event: pygame.Event):
        if self.manager.process_events(event):
            return

        if event.type == pygame.QUIT:
            self.is_running = False

        elif event.type == pygame.WINDOWSIZECHANGED:
            # prevent window from getting too small
            self.set_resolution((max(event.x, 200), max(event.y, 200)))

        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if isinstance(event.ui_element, AnchorButton):
                target = event.ui_element.anchor

                if self.dragged_anchor is not None:
                    self.dragged_anchor = None
                    return

                if self.selected_anchor == target:
                    self.select_anchor(None)
                else:
                    self.select_anchor(target)

            else:
                event.ui_element

        elif event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if isinstance(event.ui_element, AnchorButton):
                if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                    self.select_anchor(event.ui_element.anchor)
                    self.dragged_anchor = event.ui_element.anchor
                    self.dragged_anchor_pos = self.dragged_anchor.position

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.settings_window.toggle_visibility()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                self.canvas_being_dragged = True
                self.canvas_has_moved = False

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == pygame.BUTTON_LEFT:
                # if the canvas hasn't moved, we can considered the user to have simply clicked on it
                # therefore we deselect the selected anchor
                if not self.canvas_has_moved:
                    self.select_anchor(None)

        elif event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[0]:
                x_rel, y_rel = event.rel
                x_off = x_rel / self.pix_per_meter_scale
                y_off = -y_rel / self.pix_per_meter_scale

                if self.canvas_being_dragged:
                    offset = (-x_off, -y_off)
                    self.move_viewport(offset)
                    self.canvas_has_moved = True

                elif self.dragged_anchor is not None:
                    offset = (x_off, y_off)
                    self.dragged_anchor_pos = (
                        self.dragged_anchor_pos[0] + x_off,
                        self.dragged_anchor_pos[1] + y_off,
                    )

                    if pygame.key.get_pressed()[pygame.K_LCTRL]:
                        _render_pos = (
                            round(self.dragged_anchor_pos[0]),
                            round(self.dragged_anchor_pos[1]),
                        )
                    else:
                        _render_pos = self.dragged_anchor_pos

                    self.dragged_anchor.position = _render_pos

            else:
                self.canvas_being_dragged = False
                self.dragged_anchor = None

        elif event.type == pygame.MOUSEWHEEL:
            self.zoom(event.y * 20)

    def pos_to_canvas_pix(self, pos_in_meters: Tuple[float, float]):
        center_x, center_y = self.canvas.get_rect().center

        x_pos, y_pos = pos_in_meters
        c_x, c_y = self.viewport_center_pos

        x_off, y_off = x_pos - c_x, y_pos - c_y

        x_pix = x_off * self.pix_per_meter_scale + center_x
        y_pix = center_y - y_off * self.pix_per_meter_scale

        return int(x_pix), int(y_pix)

    def canvas_pix_to_pos(self, canvas_pix: Tuple[int, int]):
        center_x, center_y = self.canvas.get_rect().center

        x_can, y_can = canvas_pix
        c_x, c_y = self.viewport_center_pos

        x_off, y_off = x_can - center_x, y_can - center_y

        x_off = float(x_off) / self.pix_per_meter_scale + c_x
        y_off = -float(y_off) / self.pix_per_meter_scale + c_y

        return x_off, y_off

    def zoom(self, zoom: int):
        self.pix_per_meter_scale = int(max(self.pix_per_meter_scale + zoom, 20))

    def move_viewport(self, offset: Tuple[float, float]):
        x, y = self.viewport_center_pos
        x_off, y_off = offset
        self.viewport_center_pos = [x + x_off, y + y_off]

    def draw_grid(self):
        top_left_real_pos = self.canvas_pix_to_pos((0, 0))

        x_real, y_real = top_left_real_pos

        start_x, start_y = math.floor(x_real), math.floor(y_real)

        strength = min(self.pix_per_meter_scale + 20, 255)

        color = (strength, strength, strength)

        x_pix, y_pix = self.pos_to_canvas_pix((start_x, start_y))

        width, height = self.canvas.get_size()
        while x_pix < width:
            pygame.draw.line(self.canvas, color, (x_pix, 0), (x_pix, height), 1)
            x_pix += self.pix_per_meter_scale

        while y_pix < height:
            pygame.draw.line(self.canvas, color, (0, y_pix), (width, y_pix), 1)
            y_pix += self.pix_per_meter_scale

    def add_anchor_signal(self, signal: RssiSignal):
        bisect.insort(self.signals_sorted_by_age, signal, key=lambda s: s.get_age())

    def add_beacon_signal(self, signal: BeaconSignal):
        ssid = signal.ssid

        for a in self.anchors:
            if a.ssid == ssid:
                s = RssiSignal(a, signal.rssi, time=signal.timestamp)
                self.add_anchor_signal(s)

    def remove_old_signals(self, max_age: float = 10):
        self.signals_sorted_by_age = [
            s for s in self.signals_sorted_by_age if not s.older_than(max_age)
        ]

    async def run(self):
        sig_gen = SignalGenerator(self.add_anchor_signal, self.anchors)

        sig_reader = SignalReader(self.add_beacon_signal)

        sig_gen_task = asyncio.create_task(sig_gen.run())

        sig_reader_task = asyncio.create_task(sig_reader.run())

        average_dist: Dict[Anchor, float] = {}

        while self.is_running:
            time_delta = self.clock.tick(120) / 1000.0

            pos_box_str = ""

            # process events
            for event in pygame.event.get():
                self.process_events(event)

            self.canvas.fill((0, 0, 0))
            self.draw_grid()
            self.screen.blit(self.canvas, (0, 0))

            self.update_anchor_buttons()

            if self.settings_window.fake_signals:
                if sig_gen_task is None or sig_gen_task.cancelled():
                    sig_gen_task = asyncio.create_task(sig_gen.run())
            elif sig_gen_task is not None:
                sig_gen_task.cancel()
                sig_gen_task = None

            self.render_age = self.settings_window.render_age

            await asyncio.sleep(0)

            self.remove_old_signals(60)

            log_box_str = ""

            max_ssid_len = max(
                [len(s.origin.ssid) for s in self.signals_sorted_by_age] + [0]
            )
            for s in self.signals_sorted_by_age[0:10]:
                log_box_str += f"{s.origin.ssid : <{max_ssid_len}} | {s.strength :3.0f} dBm | {s.get_age():.2f} s\n"

            self.signal_log_box.set_text(log_box_str)

            distances_by_anchor = self.get_distances_by_anchor()

            for anchor, distances in distances_by_anchor.items():
                if len(distances) > 0:
                    average_dist[anchor] = mean(distances)

            for anchor, distance in average_dist.items():
                if self.settings_window.min_max:
                    self.draw_bounding_box_around_anchor(
                        anchor, distance, anchor.color, 1
                    )

                self.draw_circle_around_anchor(anchor, distance, anchor.color, 5)

            max_distance_by_anchor = {
                anchor: max(distances)
                for anchor, distances in distances_by_anchor.items()
            }
            if self.settings_window.min_max:
                center_x, center_y, width, height = min_max(max_distance_by_anchor)

                center = (center_x, center_y)

                pos_box_str += f"Min-Max       : {center_x:.2f}, {center_y:.2f}\n"

                self.draw_bounding_box(
                    center, width, height, (255, 255, 255), intensity=0.2, thickness=0
                )

            if self.settings_window.point_cloud:
                for x in range(0, self.canvas.get_width(), 5):
                    for y in range(0, self.canvas.get_height(), 5):
                        real_pos = self.canvas_pix_to_pos((x, y))

                        nb_anchors = 0
                        for anchor, dist in max_distance_by_anchor.items():
                            # maybe optimize with square distance
                            if math.dist(anchor.position, real_pos) < dist:
                                nb_anchors += 1

                        s = nb_anchors / len(self.anchors) * 255.0
                        pygame.draw.circle(self.screen, (s, 0, 0), (x, y), 4)

            if len(average_dist) > 0 and self.settings_window.min_max:
                center_x, center_y, width, height = min_max(average_dist)

                pos_box_str += f"Min-Max(avg)  : {center_x:.2f}, {center_y:.2f}\n"

                center = (center_x, center_y)

                self.draw_bounding_box(
                    center, width, height, (255, 255, 255), intensity=0.5, thickness=0
                )

                center = self.pos_to_canvas_pix(center)

                pygame.draw.circle(self.screen, (255, 255, 255), center, 10, 10)

            anc_dist_pairs = list(average_dist.items())[0:3]

            if len(anc_dist_pairs) == 3 and self.settings_window.trilateration:
                trilat_pos = trilaterate(*anc_dist_pairs)

                pos_box_str += (
                    f"Trilatération : {trilat_pos[0]:.2f}, {trilat_pos[1]:.2f}\n"
                )

                pygame.draw.circle(
                    self.screen,
                    (255, 255, 255),
                    self.pos_to_canvas_pix(trilat_pos),
                    10,
                    10,
                )
                
            if self.settings_window.vae:
                self.learning_settings_window.show()
            else:
                self.learning_settings_window.hide()
                
            if  (len(self.signals_sorted_by_age) > 0) and (self.settings_window.vae):
                vae.addSample(self.signals_sorted_by_age[0].origin.num, self.signals_sorted_by_age[0].strength)
                if all(vae_counter>=100):
                    vae_pos = vae.getCoord(vae.feature)
                    pos_box_str += (
                        f"VAE : {vae_pos[0]:.2f}, {vae_pos[1]:.2f}\n"
                    )
                    pygame.draw.circle(
                        self.screen,
                        (255, 255, 255),
                        self.pos_to_canvas_pix(vae_pos),
                        10,
                        10,
                    )
                else:
                    vae_counter[self.signals_sorted_by_age[0].origin.num-1] += 1
                    pos_box_str += (
                        f"VAE : waiting for enough data{vae_counter}\n"
                    )
            if (len(self.signals_sorted_by_age) > 0) and (self.settings_window.vae) and (self.learning_settings_window.learn):
                pos_to_learn = self.learning_settings_window.getCoord()
                if all(vae_counter>=100):
                    loss = vae.train(pos_to_learn[0], pos_to_learn[1], vae.feature, save=(not self.settings_window.fake_signals))
                    pos_box_str += (
                        f"VAE : train loss{ loss}\n"
                    )
                
            self.position_log_box.set_text(pos_box_str)

            self.manager.update(time_delta)
            self.manager.draw_ui(self.screen)

            pygame.display.update()

    def get_distances_by_anchor(self):
        distances_by_anchor: Dict[Anchor, List[float]] = {}

        for s in self.signals_sorted_by_age:
            self.draw_signal(s, 0.4)

            if not s.older_than(self.render_age):
                if s.origin not in distances_by_anchor:
                    distances_by_anchor[s.origin] = []

                distances_by_anchor[s.origin].append(s.esim_dist_to_anchor())
        return distances_by_anchor

    def update_anchor_buttons(self):
        for b in self.anchor_buttons:
            a = b.anchor
            b.set_center_pos(self.pos_to_canvas_pix(a.position))
            b.set_radius(self.pix_per_meter_scale // 2)

            if a is self.selected_anchor:
                b.select()
            elif b.is_selected:
                b.unselect()

        if not self.anchor_settings_window.visible:
            self.select_anchor(None)

    def draw_circle_around_anchor(self, anchor, radius, color, line_width):
        pix = self.pos_to_canvas_pix(anchor.position)
        radius *= self.pix_per_meter_scale
        pygame.draw.circle(self.screen, color, pix, radius + line_width / 2, line_width)

    def draw_bounding_box(
        self, position, width, height, color, intensity: float = 1, thickness: int = 5
    ):
        pix = self.pos_to_canvas_pix(position)
        width *= self.pix_per_meter_scale
        height *= self.pix_per_meter_scale

        color = [int(c * intensity) for c in color]

        r = Rect(pix[0] - width / 2, pix[1] - height / 2, width, height)
        pygame.draw.rect(self.screen, color, r, thickness)

    def draw_bounding_box_around_anchor(self, anchor: Anchor, radius, color, intensity):
        self.draw_bounding_box(
            anchor.position, radius * 2, radius * 2, color, intensity
        )

    def draw_signal(self, signal: RssiSignal, intensity: float = 1):
        age = signal.get_age()

        strength = max(0, 1 - age / max(1, self.render_age))
        if strength < 0.01:
            return

        line_width = int(strength * 5) + 1

        color = signal.origin.color

        color = [int(c * strength * intensity) for c in color]

        self.draw_circle_around_anchor(
            signal.origin, signal.esim_dist_to_anchor(), color, line_width
        )


import cProfile

if __name__ == "__main__":
    # cProfile.run('asyncio.run(App().run())')
    asyncio.run(App().run())
