from   dash_iconify import DashIconify
from   typing       import Any

from   ..types      import Notification

def login_success_notification(translation: dict) -> Notification:
    r'''
    Notification sent when the login succeeds.

    :param translation: dictionary containing the text to show
    '''
    
    return Notification(
        title     = translation['login']['success']['title'],
        position  = 'top-center',
        action    = 'show',
        color     = 'green',
        autoClose = 4000,
        icon      = DashIconify(icon='icon-park-outline:success')
    )

def login_username_fail_notification(translation: dict) -> Notification:
    r'''
    Notification sent when the login fails because of a wrong username.

    :param translation: dictionary containing the text to show
    '''
    
    return Notification(
        title     = translation['login']['fail']['title'],
        message   = translation['login']['fail']['username'],
        position  = 'top-center',
        action    = 'show',
        color     = 'red',
        autoClose = 4000,
        icon      = DashIconify(icon='si:error-duotone')
    )

def login_password_fail_notification(translation: dict) -> Notification:
    r'''
    Notification sent when the login fails because of a wrong password.

    :param translation: dictionary containing the text to show
    '''

    return Notification(
        title     = translation['login']['fail']['title'],
        message   = translation['login']['fail']['password'],
        position  = 'top-center',
        action    = 'show',
        color     = 'red',
        autoClose = 4000,
        icon      = DashIconify(icon='si:error-duotone')
    )

def logout_success_notification(translation: dict) -> Notification:
    r'''
    Notification sent when the login fails because of a wrong username.

    :param translation: dictionary containing the text to show
    '''
    
    return Notification(
        title     = translation['logout']['success']['title'],
        position  = 'top-center',
        action    = 'show',
        color     = 'green',
        autoClose = 4000,
        icon      = DashIconify(icon='icon-park-outline:success')
    )

def hike_upload_success_notification(translation: dict) -> Notification:
    r'''
    Notification sent when the hike upload succeeds.

    :param translation: dictionary containing the text to show
    '''
    
    return Notification(
        title     = translation['hike_upload']['success']['title'],
        position  = 'top-center',
        action    = 'show',
        color     = 'green',
        autoClose = 4000,
        icon      = DashIconify(icon='icon-park-outline:success')
    )

def hike_upload_format_fail_notification(translation: dict) -> Notification:
    r'''
    Notification sent when the hike upload fails because the file could not be loaded properly

    :param translation: dictionary containing the text to show
    '''

    return Notification(
        title     = translation['hike_upload']['fail']['title'],
        message   = translation['hike_upload']['fail']['format_error']['text'],
        position  = 'top-center',
        action    = 'show',
        color     = 'red',
        autoClose = 4000,
        icon      = DashIconify(icon='si:error-duotone')
    )

def hike_upload_already_there_fail_notification(translation: dict) -> Notification:
    r'''
    Notification sent when the hike upload fails because the file is already loaded.

    :param translation: dictionary containing the text to show
    '''

    return Notification(
        title     = translation['hike_upload']['fail']['title'],
        message   = translation['hike_upload']['fail']['already_loaded_error']['text'],
        position  = 'top-center',
        action    = 'show',
        color     = 'red',
        autoClose = 4000,
        icon      = DashIconify(icon='si:error-duotone')
    )

def wrong_magic_link_notification(translation: dict) -> Notification:
    r'''
    Notification sent when the magic link in the url is not in the database.

    :param translation: dictionary containing the text to show
    '''
    
    return Notification(
        title     = translation['magic_link']['fail']['title'],
        message   = translation['magic_link']['fail']['text'],
        position  = 'top-center',
        action    = 'show',
        color     = 'red',
        autoClose = 4000,
        icon      = DashIconify(icon='si:error-duotone')
    )

