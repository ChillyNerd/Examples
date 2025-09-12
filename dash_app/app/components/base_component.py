from abc import ABC, abstractmethod

from dash_app.app.abstract_app import AbstractApp


class BaseComponent(ABC):
    layout = None

    def __init__(self, app: AbstractApp):
        self.app = app
        self.dash_app = app.app
        self.hidden = 'component-hidden'
        self.init_callbacks()

    @abstractmethod
    def init_callbacks(self):
        pass

    def get_layout(self):
        return self.layout
