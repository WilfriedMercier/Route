import dash
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

def generate_magic_link_container_rows_from_db(
        translation : dict,
        hike_names  : list[str]
    ) -> list[dmc.Stack]:
    r'''
    Generate a list of components added into the magic link panel container.

    :param translation: translation for the UI elements
    :param hike_names: all hike names that an be toggled in the multiselect componenent. These are all hikes associated to the user.
    '''

    # By default, no color is associated to hikes shown in the multiselect
    # If None, colors are sampled from a color palette later
    color_props : dict[str, str | None] = {
        hike_name : None
        for hike_name in hike_names
    }

    # Get all magic link props associated to the user
    rows = Magic_links_props_table.get_rows_from_user_id(session['user_id'])

    # Process output to group hikes according to magic links
    magic_links = {
    }

    for magic_link, hike_id, color in rows:

        # Get hike name associated to hike ID
        hike_name = Hikes_table.get_hike_name_from_hike_id(hike_id)

        # Update color based on db table value for hikes already toggled in the magic link
        color_props[hike_name] = color

        if magic_link not in magic_links:  

            magic_link_name = Magic_links_table.get_magic_link_name(magic_link)

            magic_links[magic_link]          = {} 
            magic_links[magic_link]['hikes'] = [hike_name]
            magic_links[magic_link]['name']  = magic_link_name

        else: magic_links[magic_link]['hikes'].append(hike_name)

    children = []
    for magic_link, props in magic_links.items():

        children.append(
            magic_link_container_item(
                magic_link,
                props['name'], # XXX to be modified soon
                translation['item'],
                color_props,
                props['hikes'] 
            )
        )

    return children

def update_ui_after_single_hike_load(
        latitudes        : list[float],
        longitudes       : list[float],
        pos_absolute     : int,
        hike_name        : str,
        language_dict    : dict,
        magic_link_state : bool = False
    ) -> tuple[dmc.Space, dl.Polyline]:
    r'''
    Update components after a single hike load.

    :param latitudes: latitudes of the hike plotted on the map
    :param longitudes: longitudes of the hike plotted on the map
    :param pos_absolute: absolute index of the hike in the hike list
    :param hike_name: name of the hike
    :param language_dict: dictionary for the hikelist element
    :param magic_link_state: True triggers a special UI for magic links, False triggers the normal UI

    :returns:
        - hikelist element widget
        - PolyLine that represents the path of the hike
    '''

    color    = COLOR_PALETTE[pos_absolute]

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
            latitudes             = hike[2],
            longitudes            = hike[3],
            center_lat            = hike[4],
            center_lon            = hike[5],
            distances             = hike[6],
            elevations            = hike[7]
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
            latitudes             = hike[2],
            longitudes            = hike[3],
            center_lat            = hike[4],
            center_lon            = hike[5],
            distances             = hike[6],
            elevations            = hike[7]
        )

        property_dict[hike[1]] = inside_dict

    widgets, traces = update_ui_after_multiple_hike_loads(
        app, property_dict, [],
        language,
        magic_link_state = session['magic-link']
    )

    return property_dict, widgets, traces