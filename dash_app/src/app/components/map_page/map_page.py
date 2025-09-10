from dash import html

from dash_app.src.app.abstract_app import AbstractApp
from dash_app.src.app.components import BaseComponent
from dash_app.src.app.components.split.split import SplitPane


class MapPage(BaseComponent):

    def __init__(self, app: AbstractApp):
        super().__init__(app)
        self.layout = html.Div(
            children=[
                SplitPane(self.app).get_layout(),
            ],
        )
        self.init_callbacks()

    def init_callbacks(self):
        pass
