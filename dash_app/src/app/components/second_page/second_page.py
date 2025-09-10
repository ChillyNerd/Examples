from dash import html

from dash_app.src.app.abstract_app import AbstractApp
from dash_app.src.app.components import BaseComponent


class SecondPage(BaseComponent):

    def __init__(self, app: AbstractApp):
        super().__init__(app)
        self.layout = html.Div(
            "Тут может быть вторая страничка",
            style= {
                "position": "absolute",
                'height': 'calc(100% - 50px)',
                'width': '100%',
                'display': 'flex',
                'justifyContent': 'center',
                'alignItems': 'center',
            }
        )
        self.init_callbacks()

    def init_callbacks(self):
        pass
