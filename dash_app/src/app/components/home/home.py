import dash_bootstrap_components as dbc
from dash import dcc
from dash import html, Output, Input

from dash_app.src.app.abstract_app import AbstractApp
from dash_app.src.app.components import BaseComponent
from dash_app.src.app.components.map_page.map_page import MapPage
from dash_app.src.app.components.table_page.table_page import TablePage


class Home(BaseComponent):

    def __init__(self, app: AbstractApp):
        super().__init__(app)
        self.layout = html.Div(
            children=[
                dbc.NavbarSimple(
                    id='navbar',
                    brand='Самосвал (название нужно поменять)',
                    color='hsla(222, 8%, 25%, 1)',
                    fluid=True,
                    sticky='top',
                    children=[
                        dbc.NavItem(children=dbc.NavLink('Главная страница', href='/', className="navigation-item")),
                        dbc.NavItem(children=dbc.NavLink('Вторая страничка', href='/table', className="navigation-item")),
                    ],
                    className="navigational-bar"
                ),
                html.Div(
                    id="page-content"
                )
            ]
        )
        self.init_callbacks()
        self.map_layout = MapPage(self.app).get_layout()
        self.table_layout = TablePage(self.app).get_layout()

    def init_callbacks(self):
        @self.dash_app.callback(
            Output('page-content', 'children'),
            Input('url', 'pathname')
        )
        def redirect(url):
            if url == '/':
                return self.map_layout
            elif url == '/table':
                return self.table_layout
            else:
                return html.Div(
                    dbc.Container(
                        [
                            html.H1("404", className="display-3"),
                            html.P(
                                "Страница не найдена",
                                className="lead",
                            ),
                            html.Hr(className="my-2"),
                            dcc.Link(
                                "Вернуться на главную страницу",
                                href='/'
                            ),
                        ],
                        fluid=True,
                        className="py-3",
                    ),
                    className="p-3 bg-light rounded-3",
                )
