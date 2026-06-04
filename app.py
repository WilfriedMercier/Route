import dash
import glob
import pathlib
import argparse
import dash_bootstrap_components as     dbc
from   lib.ui                    import UI
from   lib.lang                  import load_languages, map_string_code_to_language

def main() -> None:

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
    language_files = glob.glob(str(pathlib.Path('lang') / '*.yaml'))
    languages      = [map_string_code_to_language(pathlib.Path(lang).stem) for lang in language_files]
    translations   = load_languages(languages)

    print(languages)
    ui           = UI(app, translations, map_string_code_to_language(args.language))
    app.layout   = ui.layout

    app.run(debug=True)

if __name__ == '__main__': main()