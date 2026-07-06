import dash_mantine_components as     dmc
from   dash_iconify            import DashIconify

def menubar_layout(language_dict: dict) -> dmc.AppShellNavbar:
    '''
    Initialize the layout of the menubar component.

    :param language_dict: dictionary containing the translation for the default language
    '''

    hike_panel_button = dmc.Button(
        language_dict['hike_panel_button']['text'],
        leftSection = DashIconify(icon='gis:hiker', height=28, width=28),
        id          = 'hike-panel-button',
        size        = 'md',
        variant     = 'outline',
    )

    hike_panel_button_tooltip = dmc.Tooltip(
        hike_panel_button,
        label     = language_dict['hike_panel_button']['tooltip'],
        id        = 'hike-panel-button-tooltip'
    )

    hall_of_fame_button = dmc.Button(
        language_dict['hall_of_fame_button']['text'],
        leftSection = DashIconify(icon='mdi:achievement-outline', height=28, width=28),
        id          = 'hall-of-fame-button',
        size        = 'md',
        variant     = 'outline',
        disabled    = True
    )

    hall_of_fame_button_tooltip = dmc.Tooltip(
        hall_of_fame_button,
        label    = language_dict['hall_of_fame_button']['tooltip'],
        disabled = True,
        id       = 'hall-of-fame-button-tooltip'
    )

    stack = dmc.Stack(
        [hike_panel_button_tooltip, hall_of_fame_button_tooltip],
        id = 'menubar'
    ) 

    return dmc.AppShellNavbar(
        stack,
        style = {'width' : 'fit-content'},
        id    = 'navbar'
    )