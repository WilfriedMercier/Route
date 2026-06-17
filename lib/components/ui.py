import dash_mantine_components as     dmc

from   ..lang                  import LanguageHandler
from   .                       import topbar_layout, hike_panel_layout, map_page_layout, menubar_layout

def ui_layout(hikes_data: dict, language_handler: LanguageHandler):
    r'''
    Class responsible for building the user interface of the application.
    
    :param hikes_data: dictionary containing the hike information to display
    :param language_handler: object containing the translations for all the UI components
    '''

    current_hike_name = next(iter(hikes_data.keys()), None)
    current_hike      = hikes_data[current_hike_name] if current_hike_name else None

    if current_hike is not None:
        center_lat, center_lon = current_hike['center']
        zoom                   = current_hike['zoom']
        distances              = current_hike['distances']
        elevations             = current_hike['elevations']
        color                  = current_hike['color']
    else:
        center_lat, center_lon, zoom = 45.7640, 4.8357, 10  # Default to Lyon if no hikes are loaded
        distances, elevations        = [], []
        color                        = 'black'

    topbar     = topbar_layout(language_handler['topbar'], language_handler.language)
    
    map_page   = map_page_layout(center_lat, center_lon, zoom, hikes_data)

    hike_panel = hike_panel_layout(
        {hike_name : {'color' : properties['color']} for hike_name, properties in hikes_data.items()},
        language_handler['hike_panel']
    )

    menubar = menubar_layout(language_handler['menubar'])

    #map_page.elevation_plot.add_elevation_data_to_plot(distances, elevations, color)

    return dmc.Stack(
        [
            topbar, 
            dmc.Group(
                [map_page, menubar, hike_panel],
                id = 'main-group'
            )
        ],
        id = 'main-stack',
    )