import dash
import dash_mantine_components as     dmc
from   flask                   import session
from   dash_iconify            import DashIconify

from   ..lang                  import LANGUAGE, LanguageHandler
from   ..database              import get_username

def topbar_layout(language_handler: LanguageHandler, language: LANGUAGE) -> dmc.Group:
    r'''
    Widget containing the top navigation bar of the application.
    
    :param language_handler: object containing the translation for topbar ui elements
    :param language: language of the application
    '''

    translation = language_handler[language]['topbar']

    theme_switcher_button = dmc.ColorSchemeToggle(
        lightIcon = DashIconify(icon="radix-icons:sun",  width=25, color = 'darkorange'),
        darkIcon  = DashIconify(icon="radix-icons:moon", width=25, color = 'lightblue'),
        size      = "lg",
        id        = 'theme-toggle'
    )

    theme_switcher_tooltip = dmc.Tooltip(
        theme_switcher_button,
        label     = translation['theme_switcher']['tooltip'],
        id        = 'theme-toggle-tooltip'
    )

    logo = dash.html.Img(src="/assets/logo.svg", className='logo')

    language_selector = dmc.Select(
        id         = 'language-dropdown',
        data       = [
            {
                'label': language_handler.map_language_to_dropdown_text(lang),
                'value': lang
            }
            for lang in language_handler.languages
        ],
        value      = language,  # Default selected value
        clearable         = False,
        searchable        = False,
        autoSelectOnBlur  = False,
        checkIconPosition = "right"
    )

    login_button = dmc.Button(
        translation['login_button']['text'],
        id           = 'login-button',
        rightSection = DashIconify(icon='mdi:user'),
        variant      = 'outline',
    )

    login_button_tooltip = dmc.Tooltip(
        login_button,
        id        = 'login-button-tooltip',
        label     = translation['login_button']['tooltip'], 
    )

    logout_button = dmc.Button(
        '', 
        rightSection = DashIconify(icon='mdi:logout'), 
        variant      = 'outline',
        style        = {'display' : 'none'},
        id           = 'logout-button'
    ),

    logout_button_tooltip = dmc.Tooltip(
        logout_button,
        label = translation['logout_button']['tooltip'],
        id    = 'logout-button-tooltip'
    )

    button_group = dmc.Group(
        [logout_button_tooltip, login_button_tooltip, language_selector, theme_switcher_tooltip],
        id = 'topbar-buttongroup'
    )

    return dmc.Group(
        [
            dmc.Group(
                [logo, dmc.Title('Route', order=1, className='title')], 
                id = 'logo-title-group'
            ),
            button_group
        ],
        id = 'topbar'
    )