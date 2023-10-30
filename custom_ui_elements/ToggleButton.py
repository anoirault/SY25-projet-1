from typing import Dict, Iterable, Optional, Tuple, Union
import pygame
from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface
from pygame_gui.core.ui_element import UIElement
from pygame_gui.elements import UIButton
import pygame_gui


class ToggleButton(UIButton):
    def __init__(
        self,
        relative_rect: pygame.Rect | Tuple[float, float] | pygame.Vector2,
        text: str,
        selected: bool = False,
        manager: IUIManagerInterface | None = None,
        container: IContainerLikeInterface | None = None,
        tool_tip_text: str | None = None,
        starting_height: int = 1,
        parent_element: UIElement = None, # type: ignore
        object_id: ObjectID | str | None = None,
        anchors: Dict[str, str | UIElement] = None, # type: ignore
        allow_double_clicks: bool = False,
        generate_click_events_from: Iterable[int] = frozenset([pygame.BUTTON_LEFT]),
        visible: int = 1,
        *,
        tool_tip_object_id: ObjectID | None = None,
        text_kwargs: Dict[str, str] | None = None,
        tool_tip_text_kwargs: Dict[str, str] | None = None
    ):
        super().__init__(
            relative_rect,
            text,
            manager,
            container,
            tool_tip_text,
            starting_height,
            parent_element,
            object_id,
            anchors,
            allow_double_clicks,
            generate_click_events_from,
            visible,
            tool_tip_object_id=tool_tip_object_id,
            text_kwargs=text_kwargs,
            tool_tip_text_kwargs=tool_tip_text_kwargs,
        )


    def process_event(self, event: pygame.Event) -> bool:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self:
                if self.is_selected:
                    self.unselect()
                else:
                    self.select()
        return super().process_event(event)
