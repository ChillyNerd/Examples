import dash_split_pane
from dash import html

from dash_app.src.app.abstract_app import AbstractApp
from dash_app.src.app.components import BaseComponent


class SplitPane(BaseComponent):
    def __init__(self, app: AbstractApp):
        super().__init__(app)
        split_pane = dash_split_pane.DashSplitPane(
            children=[
                html.Div(
                    children=[],
                    className='column-gap small-padding sidebar'
                ),
                html.Div(
                    children=[],
                    className='column-gap small-padding sidebar'
                )
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
        self.layout = split_pane
        self.init_callbacks()

    def init_callbacks(self):
        pass