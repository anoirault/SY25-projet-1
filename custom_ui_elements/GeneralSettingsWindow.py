import pygame
from pygame_gui.elements import UILabel, UIHorizontalSlider
from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import IUIManagerInterface
from .SettingsWindow import SettingsWindow
from .ToggleButton import ToggleButton


class GeneralSettingsWindow(SettingsWindow):
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
        self.width = width

        label_width = 40

        self.render_age: float = 5

        self.label = UILabel(pygame.Rect(0, 0, width, 20), "Settings", container=self)
        # self.fake_signals_toggle = ToggleButton(pygame.Rect(0, 0, width, 40), "Fake signals", container=self, anchors={"top_target": self.label})
        # self.trilateration_toggle = ToggleButton(pygame.Rect(0, 0, width, 40), "Trilateration", container=self, anchors={"top_target": self.fake_signals_toggle})
        # self.min_max_toggle = ToggleButton(pygame.Rect(0, 0, width, 40), "Min-Max", container=self, anchors={"top_target": self.trilateration_toggle})

        
        self.toggles = []   

        self.fake_signals_toggle  = self.add_toggle("Fake signals")
        self.trilateration_toggle = self.add_toggle("Trilateration")
        self.min_max_toggle = self.add_toggle("Min-Max")
        self.point_cloud_toggle = self.add_toggle("Point Cloud")
        self.vae_toggle = self.add_toggle("VAE")


        self.slider = UIHorizontalSlider(pygame.Rect(0, 0, width - label_width, 32), self.render_age, (1, 60), container=self, anchors={"left": "left", "right": "right", "top_target": self.toggles[-1]})
        self.slider_label = UILabel(pygame.Rect(-label_width, 0, label_width, 32), f"", container=self, anchors={"right": "right", "top_target": self.toggles[-1]})


    def add_toggle(self, title: str) -> ToggleButton:
        anchors = {"left": "left", "right": "right"}
        rect = pygame.Rect(0, 0, self.width, 40)

        if len(self.toggles) > 0:
            anchors["top_target"] = self.toggles[-1]
        else:
            rect.top = 20

        btn = ToggleButton(rect, title, container=self, anchors=anchors)
        self.toggles.append(btn)
        return btn



    @property
    def fake_signals(self) -> bool:
        return self.fake_signals_toggle.is_selected
    
    @property
    def trilateration(self) -> bool:
        return self.trilateration_toggle.is_selected
    
    @property
    def min_max(self) -> bool:
        return self.min_max_toggle.is_selected
    
    @property
    def point_cloud(self) -> bool:
        return self.point_cloud_toggle.is_selected
    
    @property
    def vae(self) -> bool:
        return self.vae_toggle.is_selected
    

    def update(self, time_delta: float):
        self.render_age = self.slider.current_value
        self.slider_label.set_text(f"{self.render_age} s")

        return super().update(time_delta)


