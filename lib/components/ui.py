import dash
import dash_mantine_components as     dmc
from   dash_extensions         import Keyboard

from ..lang import LANGUAGE, LanguageHandler
from .      import (
    topbar_layout, 
    hike_panel_layout, 
    map_page_layout, 
    menubar_layout, 
    login_modal_layout,
    magic_link_modal_layout,
    colorpicker_modal_layout,
    validate_modal_layout,
    magic_link_panel_layout
)

def ui_layout(language_handler: LanguageHandler, language: LANGUAGE) -> dash.html.Div:
    r'''
    Class responsible for building the user interface of the application.
    
    :param language_handler: object handling the translation of the UI elements
    :param language: language of the application
    '''

    translation = language_handler[language]
    
    hike_panel        = hike_panel_layout(translation['hike_panel'])
    magic_modal       = magic_link_modal_layout(translation['magic_link_modal'])
    login_modal       = login_modal_layout(translation['login_modal'])
    colorpicker_modal = colorpicker_modal_layout()
    validate_modal    = validate_modal_layout(translation['validate_modal'])
    magic_link_panel  = magic_link_panel_layout(translation['magic_link_panel'])

    appshell = appshell_layout(language_handler, language)

    return dash.html.Div([
            appshell, 
            login_modal,
            hike_panel,
            magic_modal,
            colorpicker_modal,
            validate_modal,
            magic_link_panel,
            Keyboard(id='keyboard', captureKeys=['l', 'a', 's', 'm'])
        ]
    )

def appshell_layout(language_handler: LanguageHandler, language: LANGUAGE) -> dmc.AppShell:
    r'''
    Class responsible for building the appshell part of the UI.
    
    :param language_handler: object handling the translation of the UI elements
    :param language: language of the application
    '''

    translation = language_handler[language]

    topbar      = topbar_layout(  language_handler, language)
    menubar     = menubar_layout( language_handler, language)
    map_page    = map_page_layout(language_handler, language)

    return dmc.AppShell(
        [
            topbar, 
            map_page, 
            menubar,
        ],
        header = {"height" : '4em'}, # type: ignore
        navbar = {
            "breakpoint" : 9000, 
            "collapsed"  : {"mobile": True, 'desktop' : True}, # type: ignore
            'width'      : 'fit-content'
        },
        padding = '10px',
        id      = 'appshell',
    )