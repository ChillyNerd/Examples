import dash_split_pane
from dash import html

from app.abstract_app import AbstractApp
from app.components import BaseComponent
from app.components.input.input_button_form import InputButtonForm


class FirstPage(BaseComponent):

    def __init__(self, app: AbstractApp):
        super().__init__(app)
        self.layout = dash_split_pane.DashSplitPane(
            children=[
                html.Div(
                    children=[InputButtonForm(self.app).get_layout()],
                    className='column-gap small-padding sidebar'
                ),
                html.Div(
                    children=["Тут мог бы быть контент, но его нету"],
                    style={
                        'height': '100%',
                        'width': '100%',
                        'display': 'flex',
                        'justifyContent': 'center',
                        'alignItems': 'center',
                    }
                )
            ],
            id="splitter",
            split="vertical",
            minSize=400,
            size=400,
            style={
                'padding': "0",
                'height': "calc(100% - 50px)"
            }
        )

    def init_callbacks(self):
        pass
