from   ..types import Notification
from   ..icons import IconError, IconSuccess

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
        icon      = IconSuccess()
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
        icon      = IconSuccess()
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
        icon      = IconSuccess()
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
        icon      = IconError()
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
        icon      = IconError()
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
        icon      = IconError()
    )

def share_hike_notification(translation: dict) -> Notification:
    r'''
    Notification sent when one of the the share magic link buttons is clicked in the magic link panel.

    :param translation: dictionary containing the text to show
    '''

    return Notification(
        title     = translation['share_magic_link']['title'],
        position  = 'top-center',
        action    = 'show',
        color     = 'green',
        autoClose = 4000,
        icon      = IconSuccess()
    )

def hike_title_update_notification(translation: dict) -> Notification:
    r'''
    Notification sent when one of the magic link titles in the magic link panel is updated.

    :param translation: dictionary containing the text to show
    '''

    return Notification(
        title     = translation['magic_link_title_update']['title'],
        position  = 'top-center',
        action    = 'show',
        color     = 'green',
        autoClose = 4000,
        icon      = IconSuccess()
    )