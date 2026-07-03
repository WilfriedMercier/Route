import dash_mantine_components as dmc

from ..lang import LANGUAGE, LanguageHandler
from .      import (
    topbar_layout, 
    hike_panel_layout, 
    map_page_layout, 
    menubar_layout, 
    login_modal_layout,
    magic_link_modal_layout
)

def ui_layout(language_handler: LanguageHandler, language: LANGUAGE) -> dmc.Stack:
    r'''
    Class responsible for building the user interface of the application.
    
    :param language_handler: object handling the translation of the UI elements
    :param language: language of the application
    '''

    distances, elevations        = [], []
    color                        = 'black'
    
    translation                  = language_handler[language]

    topbar      = topbar_layout(language_handler, language)
    map_page    = map_page_layout()
    hike_panel  = hike_panel_layout(translation['hike_panel'])
    menubar     = menubar_layout(translation['menubar'])
    login_modal = login_modal_layout(translation['login_modal'])
    magic_modal = magic_link_modal_layout(translation['magic_link_modal'])

    #map_page.elevation_plot.add_elevation_data_to_plot(distances, elevations, color)

    return dmc.Stack(
        [
            topbar, 
            dmc.Group([map_page, menubar, hike_panel
            ], id = 'main-group'),
            login_modal,
            magic_modal
        ],
        id = 'main-stack',
    )