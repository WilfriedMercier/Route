import dash
from   dash_iconify import DashIconify
from   typing       import Any

def login_success_notification(translation: dict) -> dict[str, Any]:
    r'''
    Notification sent when the login succeeds.

    :param translation: dictionary containing the text to show
    '''
    
    return {
        'title'     : translation['notifications']['login']['success']['title'],
        'position'  : 'top-center',
        'action'    : 'show',
        'color'     : 'green',
        'autoClose' : 4000,
        'icon'      : DashIconify(icon='icon-park-outline:success')
    }

def login_username_fail_notification(translation: dict) -> dict:
    r'''
    Notification sent when the login fails because of a wrong username.

    :param translation: dictionary containing the text to show
    '''
        
    return {
        'title'     : translation['notifications']['login']['fail']['title'],
        'position'  : 'top-center',
        'action'    : 'show',
        'message'   : translation['notifications']['login']['fail']['username'],
        'color'     : 'red',
        'autoClose' : 4000,
        'icon'      : DashIconify(icon='si:error-duotone')
    }

def login_password_fail_notification(translation: dict) -> dict:
    r'''
    Notification sent when the login fails because of a wrong password.

    :param translation: dictionary containing the text to show
    '''

    return {
        'title'     : translation['notifications']['login']['fail']['title'],
        'position'  : 'top-center',
        'action'    : 'show',
        'message'   : translation['notifications']['login']['fail']['password'],
        'color'     : 'red',
        'autoClose' : 4000,
        'icon'      : DashIconify(icon='si:error-duotone')
    }

def logout_success_notification(translation: dict) -> dict:
    r'''
    Notification sent when the login fails because of a wrong username.

    :param translation: dictionary containing the text to show
    '''
    
    return {
        'title'     : translation['notifications']['logout']['success']['title'],
        'position'  : 'top-center',
        'action'    : 'show',
        'color'     : 'green',
        'autoClose' : 4000,
        'icon'      : DashIconify(icon='icon-park-outline:success')
    }

def hike_upload_success_notification(translation: dict) -> dict:
    r'''
    Notification sent when the hike upload succeeds.

    :param translation: dictionary containing the text to show
    '''
    
    return {
        'title'     : translation['notifications']['hike_upload']['success']['title'],
        'position'  : 'top-center',
        'action'    : 'show',
        'color'     : 'green',
        'autoClose' : 4000,
        'icon'      : DashIconify(icon='icon-park-outline:success')
    }

def hike_upload_format_fail_notification(translation: dict) -> dict:
    r'''
    Notification sent when the hike upload fails because the file could not be loaded properly

    :param translation: dictionary containing the text to show
    '''
    
    return {
        'title'     : translation['notifications']['hike_upload']['fail']['title'],
        'message'   : translation['notifications']['hike_upload']['fail']['format_error']['text'],
        'position'  : 'top-center',
        'action'    : 'show',
        'color'     : 'red',
        'autoClose' : 4000,
        'icon'      : DashIconify(icon='si:error-duotone')
    }

def hike_upload_already_there_fail_notification(translation: dict) -> dict:
    r'''
    Notification sent when the hike upload fails because the file is already loaded.

    :param translation: dictionary containing the text to show
    '''
    
    return {
        'title'     : translation['notifications']['hike_upload']['fail']['title'],
        'message'   : translation['notifications']['hike_upload']['fail']['already_loaded_error']['text'],
        'position'  : 'top-center',
        'action'    : 'show',
        'color'     : 'red',
        'autoClose' : 4000,
        'icon'      : DashIconify(icon='si:error-duotone')
    }