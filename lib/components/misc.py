import dash
import dash_mantine_components as     dmc

from ..lang  import LanguageHandler, LANGUAGE
from ..types import DashID
from ..icons import (
    IconMoon,
    IconSun,
    IconCheck,
    IconLanguage,
    IconUser
)

def login_button_layout(
        id          : str,
        translation : dict,
        visibleFrom : str | None = None,
        hiddenFrom  : str | None = None,
        iconAlone   : bool = False,
    ) -> dmc.Tooltip:
    r'''
    Generate at startup a group of buttons used for login/logout.
    
    :param id: identifier of the object
    :param translation: object containing the translation for the login/logout button group
    :param visibleFrom: prop passed to the dmc.Button object to decide when to hide it base on screen's width
    :param hiddenFrom: prop passed to the dmc.Button object to decide when to hide it base on screen's width
    :param iconAlone: whether to just show the icon or icon + text
    '''

    icon   = IconUser()

    button = dmc.Button(
        icon if iconAlone else translation['text'],
        id           = {'type' : 'login-button', 'index' : id},
        rightSection = None if iconAlone else icon,
        variant      = 'outline',
        visibleFrom  = visibleFrom,
        hiddenFrom   = hiddenFrom
    )

    button_tooltip = dmc.Tooltip(
        button,
        id        = {'type' : 'login-button-tooltip', 'index' : id},
        label     = translation['tooltip'], 
    )

    return button_tooltip

def language_element(id: str, text: str, lang: LANGUAGE, checkmark: bool) -> dash.html.Div:
    r'''
    UI element in the custom language dropdown menu representing one language.

    :param id: identifier of the object
    :param text: text to display (i.e. name of the language)
    :param lang: language represented by the element
    :param checkmark: whether to display a checkmark (True if selected)
    '''

    return dash.html.Div(
        dmc.Button(
            dmc.Group([
                dmc.Text(text),
                IconCheck(style  = {'display' : 'flex' if checkmark else 'none'})
            ]),
            variant = 'subtle',
            id      = {'type': 'language-button', 'index': f'{id}-{lang}'},
        ),
        className = 'language-element',
    )

def language_selector_layout(
        id               : str,
        language_handler : LanguageHandler, 
        language         : LANGUAGE,
        visibleFrom      : str | None = None,
        hiddenFrom       : str | None = None,
    ) -> dmc.Box:
    r'''
    Widget used to switch between languages.
    
    :param id: identifier of the object
    :language_handler: object handling translation
    :param language: current language of the application
    :param visibleFrom: prop passed to the dmc.Button object to decide when to hide it base on screen's width
    :param hiddenFrom: prop passed to the dmc.Button object to decide when to hide it base on screen's width
    '''

    language_elements = []
    for lang in language_handler.languages:
        language_elements.append(language_element(
            id,
            language_handler.map_language_to_dropdown_text(lang),
            lang,
            language == lang
        ))

    stack_languages = dmc.Stack(language_elements, id = {'type' : 'language-dropdown', 'index' : id})

    hover_card = dmc.HoverCard(
        [
            dmc.HoverCardTarget(IconLanguage(), boxWrapperProps={'style' : {'display' : 'flex'}}),
            dmc.HoverCardDropdown(stack_languages)
        ],
        id = {'type' : 'language-dropdown-hovercard', 'index' : id},
    )

    return dmc.Box(hover_card, visibleFrom=visibleFrom, hiddenFrom=hiddenFrom)

def theme_switcher_layout(
        id          : str,
        visibleFrom : str | None = None,
        hiddenFrom  : str | None = None,
    ) -> dmc.ColorSchemeToggle:
    r'''
    Widget used to switch between light and dark themes.

    :param id: identifier of the object
    :param visibleFrom: prop passed to the dmc.Button object to decide when to hide it base on screen's width
    :param hiddenFrom: prop passed to the dmc.Button object to decide when to hide it base on screen's width
    '''

    return dmc.ColorSchemeToggle(
        lightIcon   = IconSun( width=25),
        darkIcon    = IconMoon(width=25),
        size        = "lg",
        visibleFrom = visibleFrom,
        hiddenFrom  = hiddenFrom,
        id          = {'type' : 'theme-toggle', 'index' : id}
    )

def custom_colorpicker(
        color: str,
        button_id : DashID,
        colorpicker_id: DashID,
        popover_id : DashID
    ) -> dmc.Popover:

    target = dmc.PopoverTarget(
        dmc.ActionIcon(
            id        = button_id, # type: ignore
            className = 'colorpicker',
            color     = color,
            size      = 'lg'
        )
    )

    dropdown = dmc.PopoverDropdown(
        dmc.ColorPicker(
            id        = colorpicker_id, # type: ignore
            fullWidth = True,
            focusable = True,
            value     = color,
        )
    )

    return dmc.Popover(
        [target, dropdown],
        id        = popover_id, # type: ignore
        width     = 200,
        withArrow = True,
    )