import dash_mantine_components as dmc

from ..lang import LANGUAGE, LanguageHandler
from .      import (
    topbar_layout, 
    hike_panel_layout, 
    map_page_layout, 
    menubar_layout, 
    login_modal_layout
)

def ui_layout(language_handler: LanguageHandler, language: LANGUAGE):
    r'''
    Class responsible for building the user interface of the application.
    
    :param langauge_handler: object handling the translation of the UI elements
    '''

    # Default to Lyon if no hikes are loaded
    center_lat, center_lon, zoom = 45.7640, 4.8357, 10
    distances, elevations        = [], []
    color                        = 'black'
    
    translation                  = language_handler[language]

    topbar      = topbar_layout(language_handler, language)
    map_page    = map_page_layout(center_lat, center_lon, zoom)
    hike_panel  = hike_panel_layout(translation['hike_panel'])
    menubar     = menubar_layout(translation['menubar'])
    login_modal = login_modal_layout(translation['login_modal'])

    #map_page.elevation_plot.add_elevation_data_to_plot(distances, elevations, color)

    return dmc.Stack(
        [
            topbar, 
            dmc.Group([map_page, menubar, hike_panel
            ], id = 'main-group'),
            login_modal
        ],
        id = 'main-stack',
    )