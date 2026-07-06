import dash_mantine_components as     dmc
from   dash_iconify            import DashIconify

def login_button_layout(translation: dict) -> dmc.Tooltip:
    r'''
    Generate at startup a group of buttons used for login/logout.
    
    :param translation: object containing the translation for the login/logout button group
    '''

    button = dmc.Button(
        translation['login']['text'],
        id           = 'login-button',
        rightSection = DashIconify(icon='mdi:user'),
        variant      = 'outline',
    )

    tooltip = dmc.Tooltip(
        button,
        id        = 'login-button-tooltip',
        label     = translation['login']['tooltip'], 
    )

    return tooltip