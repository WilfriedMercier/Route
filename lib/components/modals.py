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
        title           = language_handler['title']['text'],
        withCloseButton = True
    )

def magic_link_modal_layout(language_handler: dict) -> dmc.Modal:
    r'''
    Generate a modal that shows the newly created magic link.

    :param language_handler: object handling the translation of the UI elements
    '''

    link = dmc.CopyButton('', value=None, variant='subtle', id = 'magic-link-copy-button')

    return dmc.Modal(
        dmc.Stack([
            dmc.Text(language_handler['text'], id='magic-link-modal-text'),
            link
        ]),
        title = language_handler['title'],
        id    = 'magic-link-modal'
    )