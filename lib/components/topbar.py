import dash
import dash_bootstrap_components as     dbc
from   ..lang                    import LanguageEnum, LanguageHandler

class ThemeSwitcher:

    def __init__(self) -> None:

        self._build_layout()

        return
    
    def _build_layout(self) -> None:

        self.light_icon = dash.html.I(className="bi bi-brightness-high-fill fs-3 grey-icons")
        self.dark_icon  = dash.html.I(className="bi bi-moon-stars-fill fs-5 grey-icons")

        self.theme_button = dbc.Switch(
            id    = 'theme-toggle',
            value = False
        )

        self.layout = dash.html.Div(
            [self.light_icon, self.theme_button, self.dark_icon],
            id = 'topbar-themebutton-group'
        )

        return

class TopBar:
    r'''Class responsible for building the top navigation bar of the application.'''

    def __init__(self, app: dash.Dash, translations: dict, default_language: LanguageEnum = LanguageEnum.ENGLISH) -> None:

        self.app = app

        # Component handling the language translation for this widget
        self.language_handler = LanguageHandler(translations, default_language)

        self._build_layout()

        return
    
    def _build_layout(self) -> None:
        r'''Build the top navigation bar layout.'''

        self.theme_switcher = ThemeSwitcher()

        self.logo = dash.html.Img(src="/assets/logo.svg", className='logo')

        self.language_selector = dash.dcc.Dropdown(
            id         = 'language-dropdown',
            options    = [
                {
                    'label': self.language_handler.map_language_to_dropdown_text(lang),
                    'value': lang.value
                }
                for lang in self.language_handler.languages
            ],
            value      = self.language_handler.language.value,  # Default selected value
            clearable  = False,
            searchable = False
        )

        self.button_group = dash.html.Div(
            [self.language_selector, self.theme_switcher.layout],
            id = 'topbar-buttongroup'
        )

        self.layout = dash.html.Div(
            [
                dash.html.Div([self.logo, dash.html.H1('Route')], id='logo-title-group'),
                self.button_group
            ],
            id        = 'topbar',
            className = 'bg-light border-bottom p-3',
        )

        return