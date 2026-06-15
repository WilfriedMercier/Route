import dash
import dash_mantine_components as     dmc
from   dash_iconify            import DashIconify

from   ..lang                  import LanguageEnum, LanguageHandler

class TopBar:
    r'''
    Class responsible for building the top navigation bar of the application.
    
    :param app: the Dash application instance
    '''

    def __init__(self, app: dash.Dash) -> None:

        self._app = app

        self._init_layout()

        return
    
    @property
    def app(self) -> dash.Dash: return self._app

    @property
    def layout(self): return self._layout
    
    def _init_layout(self) -> None:
        r'''Build the top navigation bar layout.'''

        theme_switcher_button = dmc.ColorSchemeToggle(
            lightIcon = DashIconify(icon="radix-icons:sun",  width=25, color = 'darkorange'),
            darkIcon  = DashIconify(icon="radix-icons:moon", width=25, color = 'lightblue'),
            size      = "lg",
            id        = 'theme-toggle'
        )

        theme_switcher_tooltip = dmc.Tooltip(
            theme_switcher_button,
            label     = self.app.lang['topbar']['theme_switcher']['tooltip'],
            openDelay = 1000,
            id        = 'theme-toggle-tooltip'
        )

        logo = dash.html.Img(src="/assets/logo.svg", className='logo')

        language_selector = dash.dcc.Dropdown(
            id         = 'language-dropdown',
            options    = [
                {
                    'label': LanguageEnum.map_language_to_dropdown_text(lang),
                    'value': lang.value
                }
                for lang in self.app.lang.languages
            ],
            value      = self.app.lang.language.value,  # Default selected value
            clearable  = False,
            searchable = False
        )

        button_group = dmc.Group(
            [language_selector, theme_switcher_tooltip],
            id = 'topbar-buttongroup'
        )

        self._layout = dmc.Group(
            [
                dmc.Group(
                    [logo, dmc.Title('Route', order=1, className='title')], 
                    id = 'logo-title-group'
                ),
                button_group
            ],
            id = 'topbar'
        )

        return