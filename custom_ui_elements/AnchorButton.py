from typing import Dict, Iterable, Optional, Tuple, Union
import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.core.interfaces import IContainerLikeInterface, IUIManagerInterface
from pygame_gui.core.ui_element import UIElement

from Anchor import Anchor


class AnchorButton(pygame_gui.elements.UIButton):
    def __init__(self, 
                 anchor: Anchor,
                 container: Optional[IContainerLikeInterface] = None, radius: float = 50, 
                 object_id: Union[ObjectID, str, None] = None, **kwargs):
        
        super().__init__(
            relative_rect=pygame.Rect((0, 0), (radius*2, radius*2)), text="", 
            object_id=object_id,
            container=container,
            **kwargs)
        
        self.center_pos = (0, 0)

        self.anchor = anchor
        self.radius = radius
        self.shape = "ellipse"

        self.colours['normal_bg'] = pygame.Color(0, 0, 0, 0)
        self.colours['normal_border'] = pygame.Color(0, 0, 0, 0)

        self.colours['hovered_bg'].a = 127
        self.colours['hovered_border'] = self.colours['hovered_bg']

        self.colours['selected_bg'].a = 127
        self.colours['selected_border'] = self.colours['selected_bg']

        self.update_image()

        
    def update_position(self):
        self.set_relative_position((self.center_pos[0] - self.radius, self.center_pos[1] - self.radius))


    def update_image(self):
        radius = self.radius
        anchor_image = pygame.Surface((radius*2, radius*2)).convert_alpha()
        anchor_image.fill((0,0,0,0))

        pygame.draw.circle(anchor_image, self.anchor.color, (radius, radius), radius, 2)
        pygame.draw.circle(anchor_image, self.anchor.color, (radius, radius), radius/2, 1)
        pygame.draw.circle(anchor_image, self.anchor.color, (radius, radius), 1, 1)

        self.normal_image = anchor_image
        self.hovered_image = anchor_image
        self.selected_image = anchor_image

        

        self.rebuild()

    def set_center_pos(self, center_pos: Tuple[int, int]):
        if center_pos == self.center_pos: return

        self.center_pos = center_pos
        self.update_position()

    def set_radius(self, radius: int):
        if radius == self.radius: return

        self.radius = radius
        self.set_dimensions((radius * 2, radius * 2))
        self.update_position()
        self.update_image()
    

    
