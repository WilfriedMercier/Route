import dash
import typing
import dash_mantine_components as     dmc
import dash_leaflet            as     dl
from   flask                   import session

from   ..lang                   import LANGUAGE
from   ..types                  import HikeInfo
from   ..misc                   import COLOR_PALETTE
from   ..components.magic_links import magic_link_container_item
from   ..components.hike_panel  import hikelist_element_layout
from   ..database               import (
    Magic_links_props_table, 
    Hikes_table,
    Magic_links_table
)

def generate_single_magic_link_row_from_db(
        magic_link   : str,
        name         : str,
        hikes_colors : typing.Mapping[str, str | None],
        translation  : dict,
        all_hikes    : list[str]
    ) -> dmc.Stack:
    r'''
    Generate a single magic link component for the magic link panel container.

    :param magic_link: magic link
    :param name: name of the magic link as shown in the label
    :param hikes_colors: dict with checked hikes as keys and their associated color as values
    :param translation: current language for the UI
    :param all_hikes: all hike names in the user database
    '''

    return magic_link_container_item(
        magic_link,
        name,
        translation['item'],
        list(hikes_colors.keys()),
        list(hikes_colors.values()),
        all_hikes
    )

def generate_magic_link_container_rows_from_db(
        translation : dict,
        all_hikes   : list[str]
    ) -> list[dmc.Stack]:
    r'''
    Generate a list of components added into the magic link panel container.

    :param translation: translation for the UI elements
    :param all_hikes: all hike names that an be toggled in the multiselect componenent. These are all hikes associated to the user.
    '''

    # If the user is not connected, there are no children
    if 'user_id' not in session: return []

    # Get all magic link props associated to the user
    rows        = Magic_links_table.get_rows_from_user_id(session['user_id'])
    magic_links = [row[0] for row in rows]
    ml_names    = [row[1] for row in rows]

    hike_names  : list[list[str]] = []
    hike_colors : list[list[str]] = []
    
    # Find hikes in each magic link
    for magic_link in magic_links:

        # Find all hikes associated to magic link
        hike_props  = Magic_links_props_table.get_rows_from_magic_link(magic_link)
        hike_ids    = [row[0] for row in hike_props]

        hike_colors.append(
            [prop[1] for prop in hike_props]
        )

        hike_names.append(
            [row[1] for row in Hikes_table.get_rows_from_hike_ids(hike_ids, columns=['name'])]
        )

    children = []
    for magic_link, ml_name, colors, names in zip(magic_links, ml_names, hike_colors, hike_names):

        children.append(
            magic_link_container_item(
                magic_link,
                ml_name,
                translation['item'],
                names,
                colors,
                all_hikes
            )
        )

    return children

def update_ui_after_single_hike_load(
        latitudes        : list[float],
        longitudes       : list[float],
        pos_absolute     : int,
        hike_name        : str,
        color            : str,
        language_dict    : dict,
        magic_link_state : bool = False
    ) -> tuple[dmc.Space, dl.Polyline]:
    r'''
    Update components after a single hike load.

    :param latitudes: latitudes of the hike plotted on the map
    :param longitudes: longitudes of the hike plotted on the map
    :param pos_absolute: absolute index of the hike in the hike list
    :param hike_name: name of the hike
    :param color: color of the hike
    :param language_dict: dictionary for the hikelist element
    :param magic_link_state: True triggers a special UI for magic links, False triggers the normal UI

    :returns:
        - hikelist element widget
        - PolyLine that represents the path of the hike
    '''

    # Create a hike widget in the hike list
    widget   = hikelist_element_layout(
        hike_name,
        color,
        False if pos_absolute > 0 else True,
        language_dict,
        magic_link_state = magic_link_state
    )

    line = dl.Polyline(
        id          = {'type' : 'map-trace', 'index' : hike_name},
        positions   = [(la, lo) for lo, la in zip(longitudes, latitudes)],
        pathOptions = {'color' : color}
    )

    return widget, line

def update_ui_after_multiple_hike_loads(
    app              : dash.Dash,
    property_dict    : dict[str, HikeInfo],
    hike_widgets     : list,
    language         : LANGUAGE,
    magic_link_state : bool = False
) -> tuple[list[dmc.Space], list[dl.Polyline]]:
    r'''
    Generate the new UI components that must be updated after many new hike have been loaded.

    :param app: dash app
    :param property_dict: dictionary containing hike names as keys and dictionaries with hike properties as values
    :param hike_widgets: current widgets holding hikes in the hike list
    :param language_dict: dictionary for the hikelist element
    :param magic_link_state: True triggers a special UI for magic links, False triggers the normal UI

    :returns:
        - list of hike element widgets
        - list of hike traces for the map
    '''

    language_dict = app.language_handler[language]['hike_panel']
    pos_init      = len(hike_widgets)

    new_hike_widgets = []
    new_traces       = []

    for pos, (hike_name, properties) in enumerate(property_dict.items()):

        out = update_ui_after_single_hike_load(
            properties['latitudes'],
            properties['longitudes'],
            pos_init + pos,
            hike_name,
            properties['color'],
            language_dict,
            magic_link_state = magic_link_state
        )

        if out is None: continue

        new_hike_widgets.append(out[0])
        new_traces.append(out[1])

    hike_widgets.extend(new_hike_widgets)

    return hike_widgets, new_traces

def generate_hike_ui_elements_with_login(
        app      : dash.Dash, 
        language : LANGUAGE  
    ) -> tuple[dict[str, HikeInfo], list[dmc.Space], list[dl.Polyline]]:
    r'''
    Generate all the ui elements that need to be updated after login.

    :param app: dash app
    :param language: selected language

    :returns:
        - dictionary with hike information for each hike
        - list of hike element widgets
        - list of hike traces for the map
    '''

    # Query hikes database associated to the user
    hike_properties = Hikes_table.get_rows_from_user_id(session['user_id'])

    # Build the dictionary with hike properties
    property_dict = {}

    for hike in hike_properties:

        inside_dict = HikeInfo(
            latitudes  = hike[2],
            longitudes = hike[3],
            center_lat = hike[4],
            center_lon = hike[5],
            distances  = hike[6],
            elevations = hike[7],
            color      = hike[8]   
        )

        property_dict[hike[1]] = inside_dict

    widgets, traces = update_ui_after_multiple_hike_loads(
        app, property_dict, [],
        language,
        magic_link_state = session['magic-link']
    )

    return property_dict, widgets, traces

def generate_hike_ui_elements_with_hike_id(
        app      : dash.Dash, 
        language : LANGUAGE,
        hike_id  : int
    ) -> tuple[dict[str, HikeInfo], list[dmc.Space], list[dl.Polyline]]:
    r'''
    Generate all the ui elements that need to be updated if a single hike ID is provided.

    :param app: dash app
    :param language: selected language

    :returns:
        - dictionary with hike information for each hike
        - list of hike element widgets
        - list of hike traces for the map
    '''

    # Query hikes database associated to the user
    hike_properties = Hikes_table.get_row_from_hike_id(hike_id)

    # Build the dictionary with hike properties
    property_dict = {}

    for hike in hike_properties:

        inside_dict = HikeInfo(
            latitudes  = hike[2],
            longitudes = hike[3],
            center_lat = hike[4],
            center_lon = hike[5],
            distances  = hike[6],
            elevations = hike[7],
            color      = hike[8]
        )

        property_dict[hike[1]] = inside_dict

    widgets, traces = update_ui_after_multiple_hike_loads(
        app, property_dict, [],
        language,
        magic_link_state = session['magic-link']
    )

    return property_dict, widgets, traces