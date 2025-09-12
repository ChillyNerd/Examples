from dash import html, dcc
from flask import request

from app.abstract_app import AbstractApp
from app.components.base_component import BaseComponent
from app.components.home.home import Home


class Layout:

    def __init__(self, app: AbstractApp):
        self.app = app
        self.init_callbacks()

    def get_layout(self):
        layout = html.Div(
            children=[
                dcc.Location(id='url', refresh=False),
                dcc.Store(id='file_data_store'),
                Home(self.app).get_layout()
            ]
        )
        return layout

    def init_callbacks(self):
        @self.app.app.server.route('/client-close', methods=['POST'])
        def handle_client_close():
            client = request.remote_addr
            self.app.log.debug(f"Client {client} has closed application")
            self.app.delete_clients_repo(client)
            return '', 200
