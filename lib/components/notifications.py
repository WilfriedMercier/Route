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