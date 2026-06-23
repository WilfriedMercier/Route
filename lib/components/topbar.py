import dash
import dash_mantine_components as     dmc
from   dash_iconify            import DashIconify

from   ..lang                  import LanguageEnum

def topbar_layout(language_dict: dict, language: LanguageEnum) -> dmc.Group:
    r'''
    Widget containing the top navigation bar of the application.
    
    :param language_dict: dictionary containing the translation for the default language
    '''

    theme_switcher_button = dmc.ColorSchemeToggle(
        lightIcon = DashIconify(icon="radix-icons:sun",  width=25, color = 'darkorange'),
        darkIcon  = DashIconify(icon="radix-icons:moon", width=25, color = 'lightblue'),
        size      = "lg",
        id        = 'theme-toggle'
    )

    theme_switcher_tooltip = dmc.Tooltip(
        theme_switcher_button,
        label     = language_dict['theme_switcher']['tooltip'],
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
            for lang in LanguageEnum
        ],
        value      = language.value,  # Default selected value
        clearable  = False,
        searchable = False
    )

    login_button = dmc.Button(
        language_dict['login_button']['text'],
        id           = 'login-button',
        rightSection = DashIconify(icon='mdi:user'),
        variant      = 'outline',
    )

    login_button_tooltip = dmc.Tooltip(
        login_button,
        id        = 'login-button-tooltip',
        label     = language_dict['login_button']['tooltip'],
    )

    user_widget = dmc.Tooltip(
        dmc.Button(
            '', 
            rightSection = DashIconify(icon='mdi:logout'), 
            variant      = 'outline',
            style        = {'display' : 'none'},
            id           = 'logout-button'
        ),
        label = language_dict['logout_button']['tooltip'],
        id    = 'logout-button-tooltip'
    )

    button_group = dmc.Group(
        [user_widget, login_button_tooltip, language_selector, theme_switcher_tooltip],
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