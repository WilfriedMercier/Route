import dash_mantine_components as dmc

def login_modal_layout(language_handler: dict) -> dmc.Modal:
    r'''
    Generate a modal used for login.

    :param language_handler: object handling the translation of the UI elements
    '''

    user_id_input = dmc.TextInput(
        label       = language_handler['user_id_input']['label'],
        placeholder = language_handler['user_id_input']['placeholder'],
        required    = True,
        id          = 'login-modal-id-input'
    )

    user_password_input = dmc.PasswordInput(
        label       = language_handler['user_password_input']['label'],
        placeholder = language_handler['user_password_input']['placeholder'],
        required    = True,
        style       = {'font-size' : 'small'},
        id          = 'login-modal-password-input'
    )

    login_button = dmc.Button(
        'Login',
        variant = 'outline',
        id      = 'send-login-button'
    )

    return dmc.Modal(
        dmc.Stack([user_id_input, user_password_input, login_button]),
        id              = 'login-modal',
        title           = language_handler['title'],
        withCloseButton = True
    )

def magic_link_modal_layout(language_handler: dict) -> dmc.Modal:
    r'''
    Generate a modal that shows the newly created magic link.

    :param language_handler: object handling the translation of the UI elements
    '''

    link    = dmc.CopyButton('', value=None, variant='subtle', id = 'magic-link-copy-button')
    #tooltip = dmc.Tooltip(link, id='magic-link-copy-button-tooltip', label='')

    modal = dmc.Modal(
        dmc.Stack([
            dmc.Text(language_handler['text'], id='magic-link-modal-text'),
            link
        ]),
        title = language_handler['title'],
        id    = 'magic-link-modal'
    )

    return modal

def colorpicker_modal_layout() -> dmc.Modal:
    r'''Generate a modal that contains the colorpicker to change the color of a hike.'''

    return dmc.Modal(
        dmc.ColorPicker(format="rgba", fullWidth=True, id='colorpicker'),
        withCloseButton = False,
        id              = 'colorpicker-modal'
    )

def validate_modal_layout(language_handler: dict) -> dmc.Modal:
    r'''
    Generate a modal used to validate the deletion of a hike.

    :param language_handler: object handling the translation of the UI elements
    '''

    yes_button = dmc.Button(
        language_handler['yes_button']['text'], 
        variant = 'outline', 
        color   = 'red', 
        id      = 'validate-modal-yes',
    )

    no_button  = dmc.Button(
        language_handler['no_button']['text'],  
        variant = 'outline', 
        id      = 'validate-modal-no'
    )

    buttons    = dmc.Group([no_button, yes_button], justify='space-evenly')

    children   = dmc.Stack([dmc.Text(language_handler['text'], id='validate-modal-text'), buttons])

    return dmc.Modal(
        children,
        withCloseButton = False,
        title           = '',
        id              = 'validate-modal', 
    )