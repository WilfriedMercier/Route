import dash
import dash_mantine_components as     dmc
from   dash_iconify            import DashIconify

from   ..lang                  import LanguageEnum, LanguageHandler

class ThemeSwitcher:
    r'''Class defining the widget used to switch between light and dark modes.'''

    def __init__(self) -> None:

        self._init_layout()

        return
    
    def _init_layout(self) -> None:

        self.layout = dmc.MantineProvider(
            dmc.ColorSchemeToggle(
                lightIcon = DashIconify(icon="radix-icons:sun", width=20),
                darkIcon  = DashIconify(icon="radix-icons:moon", width=20),
                color     = "black",
                size      = "lg",
            )
        )

        return

class TopBar:
    r'''Class responsible for building the top navigation bar of the application.'''

    def __init__(self, app: dash.Dash, translations: dict, default_language: LanguageEnum = LanguageEnum.ENGLISH) -> None:

        self._app = app

        # Component handling the language translation for this widget
        self.language_handler = LanguageHandler(translations, default_language)

        self._init_layout()

        return
    
    @property
    def app(self) -> dash.Dash: return self._app
    
    def _init_layout(self) -> None:
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