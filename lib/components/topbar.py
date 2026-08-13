import dash
import dash_mantine_components as     dmc

from   ..lang                  import LANGUAGE, LanguageHandler
from   .misc                   import (
    login_button_layout, 
    language_selector_layout,
    theme_switcher_layout
)

def topbar_layout(language_handler: LanguageHandler, language: LANGUAGE) -> dmc.AppShellHeader:
    r'''
    Widget containing the top navigation bar of the application.
    
    :param language_handler: object containing the translation for topbar ui elements
    :param language: language of the application
    '''

    translation = language_handler[language]['topbar']

    theme_switcher_button = theme_switcher_layout('topbar', visibleFrom='md')

    theme_switcher_tooltip = dmc.Tooltip(
        theme_switcher_button,
        label     = translation['theme_switcher']['tooltip'],
        id        = 'theme-toggle-tooltip'
    )

    logo = dash.html.Img(src="/assets/logo.svg", className='logo')

    language_selector    = language_selector_layout(
        'topbar', 
        language_handler, 
        language,
        visibleFrom = 'md'
    )
    
    login_button_tooltip = login_button_layout(
        'topbar-login-button',
        language_handler[language]['login_logout_buttons']['login'],
        visibleFrom = 'md',
    )

    button_group = dmc.Group(
        [login_button_tooltip, language_selector, theme_switcher_tooltip],
        id = 'topbar-buttongroup'
    )

    burger = dmc.Burger(id='burger', opened=False)

    burger_tooltip = dmc.Tooltip(
        burger,
        label = translation['burger']['tooltip'],
        id    = 'burger-tooltip'
    )

    badge  = dmc.Badge(
        'BETA (v0.5)', 
        className = 'version-badge', 
        size      = 'lg', 
        variant   = 'dot', 
        radius    = 'xl', 
        style     = {'textTransform' : 'none'}
    )

    group = dmc.Group(
        [
            dmc.Group(
                [
                    burger_tooltip, 
                    logo, 
                    dmc.Title('Route', order=1, className='title'),
                    badge
                ], 
                id = 'logo-title-group'
            ),
            button_group
        ],
        id = 'topbar'
    )

    return dmc.AppShellHeader(group, id = 'appshell-header')