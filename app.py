import dash
import glob
import pathlib
import argparse
import dash_bootstrap_components as     dbc
import dash_mantine_components   as     dmc

from   lib.lang                  import load_languages, LanguageHandler, LanguageEnum
from   lib.callbacks             import register_callbacks
from   lib.components import ui_layout
from   lib.io import load_hikes_from_directory

TOKEN_DB = {
    "share-endpoint": ['Lyon-Miribel', 'Lamure-Belleville'],
}

def main() -> None:

    global app

    parser = argparse.ArgumentParser(
        prog='Route',
        description='A small web app that displays hike routes.',
        add_help=True
    )

    parser.add_argument('-l', '--language', dest='language', default='en', choices=['en', 'fr'], help='Language of the application.')

    args = parser.parse_args()

    external_stylesheets = [
        dbc.themes.BOOTSTRAP,
        'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css'
    ]

    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    # Find the available languages
    default_language = LanguageEnum.map_string_code_to_language(args.language)

    language_files   = glob.glob(str(pathlib.Path('lang') / '*.yaml'))

    languages        = [
        LanguageEnum.map_string_code_to_language(pathlib.Path(lang).stem) 
        for lang in language_files
    ]

    translations     = load_languages(languages)
    language_handler = LanguageHandler(translations, default_language=default_language)

    hikes_data = load_hikes_from_directory()
    hikes_data_for_store = {
        name : {
            'zoom'   : data['zoom'],
            'center' : [data['center'][0], data['center'][1]]
        } for name, data in hikes_data.items()
    }

    app.layout   = dmc.MantineProvider(
        dash.html.Div([
            dash.dcc.Location(id='url', refresh=False),
            dash.dcc.Store(id='number_hikes', data=len(hikes_data)),
            dash.dcc.Store(id='hikes_info', data = hikes_data_for_store),
            dash.html.Div(
                ui_layout(hikes_data, language_handler),
                id = 'content-display')
        ]),
        theme={"primaryColor": "blue"}
    )

    register_callbacks(app, language_handler, TOKEN_DB)

    app.run(debug=True)

if __name__ == '__main__': main()