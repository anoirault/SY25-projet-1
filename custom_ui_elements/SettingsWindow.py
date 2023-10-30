import pygame_gui as pg_gui

class SettingsWindow(pg_gui.elements.UIWindow):
    def on_close_window_button_pressed(self):
        self.hide()


    def toggle_visibility(self):
        if self.visible:
            self.hide()
        else:
            self.show()