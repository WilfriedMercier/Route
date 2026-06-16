import dash
import glob
import pathlib
import argparse
import dash_bootstrap_components as     dbc
import dash_mantine_components   as     dmc
from   lib.ui                    import UI
from   lib.io                    import load_hikes_from_directory
from   lib.lang                  import load_languages, LanguageHandler, LanguageEnum

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
    default_language = LanguageEnum.map_string_code_to_language(args.language)

    language_files   = glob.glob(str(pathlib.Path('lang') / '*.yaml'))

    languages        = [
        LanguageEnum.map_string_code_to_language(pathlib.Path(lang).stem) 
        for lang in language_files
    ]

    translations     = load_languages(languages)

    app.lang     = LanguageHandler( # type: ignore
        translations, default_language=default_language
    )

    hikes_data     = load_hikes_from_directory() 

    app.hikes_data = hikes_data # type: ignore

    ui           = UI(app, hikes_data)
    app.ui       = ui # type: ignore
    app.layout   = dmc.MantineProvider(
        ui.layout,
        theme={"primaryColor": "blue"}
    )

    

    app.run(debug=True)

if __name__ == '__main__': main()