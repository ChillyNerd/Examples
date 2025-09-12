import dash_bootstrap_components as dbc
from dash import dcc, html, Output, Input, State
from dash.exceptions import PreventUpdate
from flask import request

from dash_app.app.abstract_app import AbstractApp
from dash_app.app.assets.icons import delete_icon
from dash_app.app.components import BaseComponent


class InputButtonForm(BaseComponent):
    def __init__(self, app: AbstractApp):
        super().__init__(app)
        upload_button = dcc.Upload(dbc.Button('Загрузить файл', className="common-button upload-button"), id='upload_file')
        delete_button = dbc.Button(
            html.Img(src=delete_icon, className='common-icon'),
            id='delete_file', className='action-button align-center delete-button'
        )
        buttons = html.Div(children=[upload_button, delete_button], className='row-gap')
        file_name = html.Div('Выберите файл', id='file_name', className="file-name")
        form = html.Div(children=[buttons, file_name], className="upload-form row-gap long-gap")
        self.layout = form

    def init_callbacks(self):
        @self.dash_app.callback([
            Output('file_name', 'children')
        ], [
            Input('upload_file', 'contents'),
            State('upload_file', 'filename')
        ])
        def upload_file(file_content, file_name):
            if not file_name:
                return ['Выберите файл']
            try:
                file = {'filename': file_name, 'content': file_content}
                self.app.upload_file(request.remote_addr, 'file_input', file)
                self.app.log.info(f'{request.remote_addr} successfully uploaded file {file_name}')
                return [file_name]
            except Exception as ex:
                self.app.log.exception(ex)
                return ['Выберите файл']

        @self.dash_app.callback(
            [
                Output('upload_file', 'contents'),
                Output('upload_file', 'filename')
            ], [
                Input('delete_file', 'n_clicks')
            ])
        def clear_excel_file(clicks):
            if clicks:
                self.app.delete_files(request.remote_addr, 'file_input')
                return None, None
            else:
                raise PreventUpdate
