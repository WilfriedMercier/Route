import dash
import yaml
import dash_mantine_components as     dmc

from   ..lang                  import LANGUAGE, LanguageHandler
from   .misc                   import (
    login_button_layout, 
    language_selector_layout,
    theme_switcher_layout
)

with open('configuration.yaml') as f: CONFIG = yaml.load(f, Loader=yaml.SafeLoader)

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

    logo = dash.html.Img(src=CONFIG['logo'], className='logo')

    language_selector = language_selector_layout(
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
        CONFIG['version'], 
        className   = 'version-badge', 
        size        = 'lg', 
        variant     = 'dot', 
        radius      = 'xl', 
        style       = {'textTransform' : 'none'},
        visibleFrom = 'sm'
    )

    hike_title = dmc.Title(
        '',
        id    = 'hike-super-title', 
        order = 3, 
        style = {'maxWidth' : '40%', 'overflow' : 'scroll', 'textWrap' : 'nowrap'}
    )

    group = dmc.Group(
        [
            dmc.Group(
                [
                    burger_tooltip, 
                    logo, 
                    dmc.Title(CONFIG['title'], order=1, className='title', visibleFrom='sm'),
                    badge
                ], 
                id = 'logo-title-group'
            ),
            hike_title,
            button_group
        ],
        id = 'topbar'
    )

    return dmc.AppShellHeader(group, id = 'appshell-header')