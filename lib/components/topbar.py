import dash
import dash_mantine_components as     dmc
from   dash_iconify            import DashIconify

from   ..lang                  import LANGUAGE, LanguageHandler

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

    language_selector = language_selector_widget(language_handler, language)

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

def language_element(text: str, lang: LANGUAGE, checkmark: bool) -> dash.html.Div:
    r'''
    UI element in the custom language dropdown menu representing one language.

    :param text: text to display (i.e. name of the language)
    :param lang: language represented by the element
    :param checkmark: whether to display a checkmark (True if selected)
    '''

    return dash.html.Div(
        dmc.Button(
            dmc.Group([
                dmc.Text(text),
                DashIconify(
                    icon   = 'material-symbols:check', 
                    style  = {'display' : 'flex' if checkmark else 'none'},
                    id     = {'type' : 'language-button-checkmark', 'index' : lang}
                )]
            ),
            variant = 'subtle',
            id      = {'type': 'language-button', 'index': lang},
        ),
        className = 'language-element',
    )
        

def language_selector_widget(language_handler: LanguageHandler, language: LANGUAGE) -> dmc.HoverCard:

    language_elements = []
    for lang in language_handler.languages:
        language_elements.append(language_element(
            language_handler.map_language_to_dropdown_text(lang),
            lang,
            language == lang
        ))

    stack_languages = dmc.Stack(language_elements, id = 'language-dropdown')

    hover_card = dmc.HoverCard(
        [
            dmc.HoverCardTarget(DashIconify(icon='mdi:language', width=20)),
            dmc.HoverCardDropdown(stack_languages)
        ],
        id = 'language-dropdown-hovercard'
    )

    return hover_card