from typing import Optional, Union
import pygame
from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import IUIManagerInterface
from custom_ui_elements.FloatEntryBox import FloatEntryBox
from .SettingsWindow import SettingsWindow
from .ToggleButton import ToggleButton
from pygame_gui.elements import UITextBox, UIWindow

import pygame_gui

from Anchor import Anchor

from pygame import Event, Rect


def try_to_float_else(string: str, default: float):
    try:
        return float(string)
    except ValueError:
        return default


class AnchorSettingsWindow(SettingsWindow):
    def __init__(
        self,
        rect: pygame.Rect,
        anchor: Optional[Anchor] = None,
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

        self.text_box = UITextBox("text", pygame.Rect(0, 0, width, -1), container=self)

        self.pos_x_input = FloatEntryBox(Rect(0, 50, width / 2, -1), container=self)
        self.pos_y_input = FloatEntryBox(
            Rect(width / 2, 50, width / 2, -1), container=self
        )

        self.m_input = FloatEntryBox(Rect(0, 100, width / 2, -1), container=self)
        self.n_input = FloatEntryBox(
            Rect(width / 2, 100, width / 2, -1), container=self
        )

        self._anchor: Optional[Anchor] = None
        self._previous_pos = None

        self.set_anchor(anchor)


    def set_anchor(self, anchor: Optional[Anchor]):
        self._anchor = anchor

        if anchor is None:
            self.text_box.set_text("none")

            self.pos_x_input.disable()
            self.pos_y_input.disable()

            self.pos_x_input.set_text("")
            self.pos_y_input.set_text("")
        else:
            self.text_box.set_text(anchor.name)

            self.pos_x_input.enable()
            self.pos_y_input.enable()
            self.m_input.enable()
            self.n_input.enable()

            self.pos_x_input.set_value(float(anchor.position[0]))
            self.pos_y_input.set_value(float(anchor.position[1]))
            self.m_input.set_value(float(anchor.m))
            self.n_input.set_value(float(anchor.n))

    def process_event(self, event: Event) -> bool:
        if self._anchor is None:
            return super().process_event(event)

        anchor = self._anchor
        old_pos = anchor.position

        if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            entry_box: FloatEntryBox = event.ui_element
            text = entry_box.get_text()

            if event.ui_element == self.pos_x_input:
                value = try_to_float_else(text, old_pos[0])
                anchor.position = (value, old_pos[1])

                entry_box.set_value(value)

            if event.ui_element == self.pos_y_input:
                value = try_to_float_else(text, old_pos[1])
                anchor.position = (old_pos[0], value)

                entry_box.set_value(value)

            if event.ui_element == self.m_input:
                value = try_to_float_else(text, anchor.m)
                anchor.m = value

                entry_box.set_value(value)

            if event.ui_element == self.n_input:
                value = try_to_float_else(text, anchor.n)
                anchor.n = value

                entry_box.set_value(value)

        if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            emtry_box: FloatEntryBox = event.ui_element
            text = emtry_box.get_text()

            if event.ui_element == self.pos_x_input:
                value = try_to_float_else(text, old_pos[0])
                anchor.position = (value, old_pos[1])

            if event.ui_element == self.pos_y_input:
                value = try_to_float_else(text, old_pos[1])
                anchor.position = (old_pos[0], value)

            if event.ui_element == self.m_input:
                value = min(try_to_float_else(text, anchor.m), 0)
                anchor.m = value

            if event.ui_element == self.n_input:
                value = max(1, try_to_float_else(text, anchor.n))
                anchor.n = value

        return super().process_event(event)
    

    def update(self, time_delta: float):
        if self._anchor is not None and self._previous_pos != self._anchor.position:
            pos = self._anchor.position
            self._previous_pos = pos
            self.pos_x_input.set_value(pos[0])
            self.pos_y_input.set_value(pos[1])
        return super().update(time_delta)
