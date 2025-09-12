from dash import html

from dash_app.app.abstract_app import AbstractApp
from dash_app.app.components import BaseComponent


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

    def init_callbacks(self):
        pass
