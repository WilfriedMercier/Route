import dash
import dash_mantine_components as     dmc
from   dash_iconify            import DashIconify

from   ..lang                  import LanguageEnum, LanguageHandler

class TopBar:
    r'''
    Class responsible for building the top navigation bar of the application.
    
    :param app: The Dash application instance.
    :param translations: A dictionary containing translations for different languages.
    :param default_language: default language used when the application starts
    '''

    def __init__(self, app: dash.Dash, translations: dict, default_language: LanguageEnum = LanguageEnum.ENGLISH) -> None:

        self._app = app

        # Component handling the language translation for this widget
        self._language_handler = LanguageHandler(translations, default_language)

        self._init_layout()

        return
    
    @property
    def app(self) -> dash.Dash: return self._app

    @property
    def language_handler(self): return self._language_handler
    
    def _init_layout(self) -> None:
        r'''Build the top navigation bar layout.'''

        self.theme_switcher_button = dmc.ColorSchemeToggle(
            lightIcon = DashIconify(icon="radix-icons:sun", width=20),
            darkIcon  = DashIconify(icon="radix-icons:moon", width=20),
            color     = "black",
            size      = "lg",
            id        = 'theme-toggle'
        )

        self.theme_switcher_tooltip = dmc.Tooltip(
            self.theme_switcher_button,
            label = self.language_handler['theme_switcher']['tooltip'],
            id    = 'theme-toggle-tooltip'
        )

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

        self.button_group = dmc.Group(
            [self.language_selector, self.theme_switcher_tooltip],
            id = 'topbar-buttongroup'
        )

        self.layout = dmc.Group(
            [
                dmc.Group([self.logo, dash.html.H1('Route')], id='logo-title-group'),
                self.button_group
            ],
            id        = 'topbar',
            className = 'bg-light border-bottom p-3',
        )

        return
    
    def update_layout_language(self, lang: LanguageEnum) -> None:
        r'''
        Update the language of the elements in the layout.

        :param: new language to apply
        '''

        self._language_handler.language = lang