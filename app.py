import dash
import flask
import glob
import secrets
import pathlib
import argparse
import datetime
import dash_mantine_components   as     dmc

from   lib.types                 import EMPTY_HIKE_DATA_FOR_MAP, EMPTY_HIKE_DATA_FOR_PLOT
from   lib.lang                  import load_languages, LanguageHandler, LANGUAGE, are_languages_correct
from   lib.callbacks             import register_callbacks
from   lib.components            import ui_layout

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
dmc.add_figure_templates()

app               = dash.Dash(__name__, server=server, external_stylesheets=None) # type: ignore

default_language: LANGUAGE = args.language.lower()

language_files   = glob.glob(str(pathlib.Path('lang') / '*.yaml'))
languages        = are_languages_correct([pathlib.Path(lang_file).stem.lower() for lang_file in language_files])
translations     = load_languages(languages)

app.language_handler = LanguageHandler(translations) # type: ignore

language = dash.dcc.Store(id='language', data=default_language)

# Default translation at startup
translation = app.language_handler[default_language]

register_callbacks(app)

# Define layout of the application
app.layout   = dmc.MantineProvider(
    dash.html.Div([
        dash.dcc.Location(id='url', refresh=False),
        dash.dcc.Store(   id='number-hikes',                   data = 0),
        dash.dcc.Store(   id='hikes-info',                     data = []), # type: ignore
        dash.dcc.Store(   id='base-url',                       data = ''),
        dash.dcc.Store(   id='colorpicker-selected-id',        data = ''),
        dash.dcc.Store(   id='selected-hike-props',            data = {}),  # Contains the following properties: index, hike name, color
        dash.dcc.Store(   id='selected-hike-data-for-plot',    data = EMPTY_HIKE_DATA_FOR_PLOT), # Contains the distances and elevations for the bottom elevation plot # type: ignore
        dash.dcc.Store(   id='selected-hike-data-for-marker',  data = EMPTY_HIKE_DATA_FOR_MAP),  # Contains the lat, lon arrays for the map figure # type: ignore
        dash.dcc.Store(   id='marker-location',                data = (0, 0)), # Contains the (lat, lon) location of the marker on the map
        dash.dcc.Store(   id='magic-link',                     data = None), # magic link used to render in a second pass the UI with or without a magic link. None is the default value at startup. During the first UI render pass, if set to '', no magic link is used, otherwise the provided magic link is used
        dash.dcc.Store(   id='dummy',                          data = {'n_clicks' : 0, 'type' : ''}), # Dummy variable used to trigger secondary callbacks after a first callback has completed
        language,
        dmc.NotificationContainer(id="notification-container"),
        ui_layout(app.language_handler, default_language),
    ]),
    theme={
        "primaryColor" : "blue", 
        'breakpoints'  : {'md' : '450px'}
    }
)


app.run(debug=True)