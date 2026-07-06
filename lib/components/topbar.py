import dash
import dash_mantine_components as     dmc
from   dash_iconify            import DashIconify

from   ..lang                  import LANGUAGE, LanguageHandler
from   .misc                   import login_button_layout

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

    language_selector    = language_selector_widget(language_handler, language)
    login_button_tooltip = login_button_layout(translation = language_handler[language]['login_logout_buttons'])

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