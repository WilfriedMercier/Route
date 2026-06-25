import dash
import flask
import glob
import secrets
import dotenv
import pathlib
import argparse
import dash_mantine_components   as     dmc

from   lib.lang                  import load_languages, LanguageHandler, LANGUAGE, are_languages_correct
from   lib.callbacks             import register_callbacks
from   lib.components            import (
    ui_layout, 
    login_success_notification,
    login_username_fail_notification,
    login_password_fail_notification,
    logout_success_notification
)

TOKEN_DB = {
    "share-endpoint": ['Lyon-Miribel', 'Lamure-Belleville'],
}

# Load environment variables for database
dotenv.load_dotenv()

'''
external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css'
]
'''

# Parse command-line arguments
parser = argparse.ArgumentParser(
    prog        = 'Route',
    description = 'A small web app that displays hike routes.',
    add_help    = True
)

parser.add_argument('-l', '--language', dest='language', default='en', choices=['en', 'fr'], help='Language of the application.')
args = parser.parse_args()

# Setup flask server and dash application
server            = flask.Flask(__name__)
server.secret_key = secrets.token_hex(32)  # Strong secret key
app               = dash.Dash(__name__, server=server, external_stylesheets=None)

default_language: LANGUAGE = args.language.lower()

language_files   = glob.glob(str(pathlib.Path('lang') / '*.yaml'))
languages        = are_languages_correct([pathlib.Path(lang_file).stem.lower() for lang_file in language_files])
translations     = load_languages(languages)

app.language_handler = LanguageHandler(translations) # type: ignore

# XXX Load hikes (temporary)
'''
hikes_data = load_hikes_from_directory()
hikes_data_for_store = {
    name : {
        'zoom'   : data['zoom'],
        'center' : [data['center'][0], data['center'][1]]
    } for name, data in hikes_data.items()
}
'''

language = dash.dcc.Store(id='language', data=default_language)

language_store = [
    language,

]

# Default translation at startup
translation          = app.language_handler[default_language]

notification_store = [
    dash.dcc.Store(id = 'login-success-notification',       data = login_success_notification(translation)),
    dash.dcc.Store(id = 'login-username-fail-notification', data = login_username_fail_notification(translation)),
    dash.dcc.Store(id = 'login-password-fail-notification', data = login_password_fail_notification(translation)),
    dash.dcc.Store(id = 'logout-success-notification',      data = logout_success_notification(translation)),
]

# Define layout of the application
app.layout   = dmc.MantineProvider(
    dash.html.Div([
        dash.dcc.Location(id='url', refresh=False),
        dash.dcc.Store(id='number_hikes', data = 0),
        dash.dcc.Store(id='hikes_info',   data = {}),
        *language_store,
        *notification_store,
        dmc.NotificationContainer(id="notification-container"),
        dash.html.Div(
            ui_layout(app.language_handler, default_language),
            id = 'content-display'
        )
    ]),
    theme={"primaryColor": "blue"}
)

# Register all callbacks and run the application
register_callbacks(app, TOKEN_DB)
app.run(debug=True)