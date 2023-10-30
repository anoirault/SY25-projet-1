import pygame
from pygame import Event, Rect
from pygame_gui.core import ObjectID, UIElement
from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface
from pygame_gui.elements import UITextEntryLine


from typing import Dict, Tuple


class FloatEntryBox(UITextEntryLine):
    def __init__(
        self,
        relative_rect: Rect | Tuple[int, int, int, int],
        value: float = 0,
        manager: IUIManagerInterface | None = None,
        container: IContainerLikeInterface | None = None,
        parent_element: UIElement | None = None,
        object_id: ObjectID | str | None = None,
        anchors: Dict[str, str | UIElement] | None = None,
        visible: int = 1,
        *,
        initial_text: str | None = None,
    ):
        super().__init__(
            relative_rect,
            manager,
            container,
            parent_element,
            object_id,
            anchors,
            visible,
            initial_text=initial_text,
            placeholder_text="",
        )

        self._value: float = value

    def set_value(self, value: float):
        value = float(value)
        self._value = value
        self.set_text(f"{value:.3}")

    def process_event(self, event: Event) -> bool:
        if self.is_focused:
            if event.type == pygame.KEYDOWN:
                fake_down_event = pygame.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN})
                fake_up_event = pygame.Event(pygame.KEYUP, {"key": pygame.K_RETURN})
                value = self._value
                if event.key == pygame.K_DOWN:
                    self.set_value(value - 0.1)
                    super().process_event(fake_down_event)
                    super().process_event(fake_up_event)

                elif event.key == pygame.K_UP:
                    self.set_value(value + 0.1)
                    super().process_event(fake_down_event)
                    super().process_event(fake_up_event)

        return super().process_event(event)