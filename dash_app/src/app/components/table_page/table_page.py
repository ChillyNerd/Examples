import dash_split_pane
from dash import html

from dash_app.src.app.abstract_app import AbstractApp
from dash_app.src.app.components import BaseComponent


class TablePage(BaseComponent):

    def __init__(self, app: AbstractApp):
        super().__init__(app)
        self.layout = dash_split_pane.DashSplitPane(
            children=[
                html.Div("HEhe"),
                html.Div("Haha"),
            ],
            id="splitter",
            split="vertical",
            minSize=400,
            size=400,
            maxSize=600,
            style={
                'padding': "0",
                'height': "calc(100% - 50px)"
            }
        )
        self.init_callbacks()

    def init_callbacks(self):
        pass
