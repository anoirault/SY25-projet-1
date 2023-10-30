from typing import Optional, Union
import pygame
from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import IUIManagerInterface
from custom_ui_elements.FloatEntryBox import FloatEntryBox
from .SettingsWindow import SettingsWindow
from .ToggleButton import ToggleButton
from pygame_gui.elements import UITextBox, UIWindow

import pygame_gui

from pygame import Event, Rect


def try_to_float_else(string: str, default: float):
    try:
        return float(string)
    except ValueError:
        return default


class LearningSettingsWindow(SettingsWindow):
    def __init__(
        self,
        rect: pygame.Rect,
        manager: IUIManagerInterface | None = None,
        window_display_title: str = "",
        element_id: str | None = None,
        object_id: ObjectID | str | None = None,
        resizable: bool = True,
        visible: int = 1,
        draggable: bool = True,
    ):
        super().__init__(
            rect,
            manager,
            window_display_title,
            element_id,
            object_id,
            resizable,
            visible,
            draggable,
        )

        width = rect.width - 32
                
        self.toggles = []   

        self.text_box = UITextBox("Coord to learn", pygame.Rect(0, 0, width, -1), container=self)

        self.pos_x_input = FloatEntryBox(Rect(0, 50, width / 2, -1), container=self)
        self.pos_y_input = FloatEntryBox(
            Rect(width / 2, 50, width / 2, -1), container=self
        )
        
        self.pos_x_input.set_text("0")
        self.pos_y_input.set_text("0")
        
        
        self.learn_toggle = self.add_toggle("Learn")


    def add_toggle(self, title: str) -> ToggleButton:
        anchors = {"left": "left", "right": "right"}
        rect = pygame.Rect(0, 0, 200, 40)

        if len(self.toggles) > 0:
            anchors["top_target"] = self.toggles[-1]
        else:
            rect.top = 100

        btn = ToggleButton(rect, title, container=self, anchors=anchors)
        self.toggles.append(btn)
        return btn
    def getCoord(self):
        x = self.pos_x_input.get_text()
        y = self.pos_y_input.get_text()
        
        return try_to_float_else(x, 0), try_to_float_else(y, 0)
    @property
    def learn(self) -> bool:
        return self.learn_toggle.is_selected