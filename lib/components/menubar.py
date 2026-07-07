import dash_mantine_components as     dmc
from   dash_iconify            import DashIconify

from   ..lang import LanguageHandler, LANGUAGE
from   .misc  import login_button_layout, language_selector_widget

def menubar_layout(language_handler: LanguageHandler, language: LANGUAGE) -> dmc.AppShellNavbar:
    '''
    Initialize the layout of the menubar component.

    :param language_handler: object containing the translation for topbar ui elements
    :param language: language of the application
    '''

    translation = language_handler[language]

    login_button = login_button_layout(
        'menubar-login-button',
        translation['login_logout_buttons']['login'],
        iconAlone   = False,
        hiddenFrom  = 'md'
    )

    language_selector = language_selector_widget(
        'menubar', 
        language_handler, 
        language,
        hiddenFrom  = 'md'
    )

    top_group = dmc.Group([login_button, language_selector], style={'justify-content' : 'space-between'})

    hike_panel_button = dmc.Button(
        translation['menubar']['hike_panel_button']['text'],
        leftSection = DashIconify(icon='gis:hiker', height=28, width=28),
        id          = 'hike-panel-button',
        size        = 'md',
        variant     = 'outline',
        fullWidth   = True,
        className   = 'menubar-button'
    )

    hike_panel_button_tooltip = dmc.Tooltip(
        hike_panel_button,
        label     = translation['menubar']['hike_panel_button']['tooltip'],
        id        = 'hike-panel-button-tooltip',
    )

    hall_of_fame_button = dmc.Button(
        translation['menubar']['hall_of_fame_button']['text'],
        leftSection = DashIconify(icon='mdi:achievement-outline', height=28, width=28),
        id          = 'hall-of-fame-button',
        size        = 'md',
        variant     = 'outline',
        disabled    = True,
        fullWidth   = True,
        className   = 'menubar-button'
    )

    hall_of_fame_button_tooltip = dmc.Tooltip(
        hall_of_fame_button,
        label    = translation['menubar']['hall_of_fame_button']['tooltip'],
        disabled = True,
        id       = 'hall-of-fame-button-tooltip'
    )

    stack = dmc.Stack(
        [top_group, dmc.Divider(hiddenFrom='md'), hike_panel_button_tooltip, hall_of_fame_button_tooltip],
        id    = 'menubar',
        style = {'width' : '100%'}
    ) 

    return dmc.AppShellNavbar(
        stack,
        withBorder = True,
        id         = 'navbar',
        w          = '300px'
    )