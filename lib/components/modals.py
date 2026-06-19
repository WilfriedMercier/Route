import dash_mantine_components as dmc

def login_modal_layout(language_handler: dict) -> dmc.Modal:

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