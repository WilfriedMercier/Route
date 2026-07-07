import dash
import dash_mantine_components as     dmc
from   dash_iconify            import DashIconify

from   ..lang                  import LANGUAGE, LanguageHandler
from   .misc                   import login_button_layout, language_selector_widget

def topbar_layout(language_handler: LanguageHandler, language: LANGUAGE) -> dmc.AppShellHeader:
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

    language_selector    = language_selector_widget(
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

    group = dmc.Group(
        [
            dmc.Group(
                [burger, logo, dmc.Title('Route', order=1, className='title')], 
                id = 'logo-title-group'
            ),
            button_group
        ],
        id = 'topbar'
    )

    return dmc.AppShellHeader(group, id = 'appshell-header')