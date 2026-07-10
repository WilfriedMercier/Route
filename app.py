import dash
import flask
import glob
import secrets
import pathlib
import argparse
import datetime
import dash_mantine_components   as     dmc

from   lib.lang                  import load_languages, LanguageHandler, LANGUAGE, are_languages_correct
from   lib.callbacks             import register_callbacks
from   lib.components            import (
    ui_layout, 
    login_success_notification,
    login_username_fail_notification,
    login_password_fail_notification,
    logout_success_notification,
    hike_upload_success_notification,
    hike_upload_format_fail_notification,
    hike_upload_already_there_fail_notification,
    wrong_magic_link_notification
)

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
server.config["SESSION_COOKIE_HTTPONLY"]      = True
server.config["SESSION_COOKIE_SAMESITE"]      = "Lax"
server.config["SESSION_PERMANENT"]            = True
server.config["SESSION_REFRESH_EACH_REQUEST"] = True
server.config["PERMANENT_SESSION_LIFETIME"]   = datetime.timedelta(hours=1)  # Session expires after 1 hour of inactivity

dmc.pre_render_color_scheme()

app               = dash.Dash(__name__, server=server, external_stylesheets=None) # type: ignore

default_language: LANGUAGE = args.language.lower()

language_files   = glob.glob(str(pathlib.Path('lang') / '*.yaml'))
languages        = are_languages_correct([pathlib.Path(lang_file).stem.lower() for lang_file in language_files])
translations     = load_languages(languages)

app.language_handler = LanguageHandler(translations) # type: ignore

language = dash.dcc.Store(id='language', data=default_language)

# Default translation at startup
translation = app.language_handler[default_language]

notification_store = [
    dash.dcc.Store(id = 'login-success-notification',       data = login_success_notification(translation)),
    dash.dcc.Store(id = 'login-username-fail-notification', data = login_username_fail_notification(translation)),
    dash.dcc.Store(id = 'login-password-fail-notification', data = login_password_fail_notification(translation)),
    dash.dcc.Store(id = 'logout-success-notification',      data = logout_success_notification(translation)),
    dash.dcc.Store(id = 'hike-load-success-notification',   data = hike_upload_success_notification(translation)),
    dash.dcc.Store(id = 'hike-load-format-fail-notification', data = hike_upload_format_fail_notification(translation)),
    dash.dcc.Store(id = 'hike-load-already-there-fail-notification', data = hike_upload_already_there_fail_notification(translation)),
    dash.dcc.Store(id = 'wrong-magic-link-notification', data = wrong_magic_link_notification(translation))
]

register_callbacks(app)

# Define layout of the application
app.layout   = dmc.MantineProvider(
    dash.html.Div([
        dash.dcc.Location(id='url', refresh=False),
        dash.dcc.Store(id='number-hikes', data = 0),
        dash.dcc.Store(id='hikes-info',   data = {}),
        dash.dcc.Store(id='hike-names-list', data = []),
        dash.dcc.Store(id='base-url', data=''),
        dash.dcc.Store(id='colorpicker-selected-id', data=None),
        dash.dcc.Store(id='selected-hike', data=None),
        dash.dcc.Store(id='map-bounds', data=None),
        language,
        *notification_store,
        dmc.NotificationContainer(id="notification-container"),
        ui_layout(app.language_handler, default_language),
    ]),
    theme={"primaryColor": "blue", 'breakpoints' : {'md' : '450px'}}
)


app.run(debug=True)